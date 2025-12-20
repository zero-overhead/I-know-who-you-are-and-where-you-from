#!/usr/bin/perl -wT
use strict;
use warnings;
use CGI qw(:standard);
use CGI::Cookie;
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);

#where to store the output files
my $basedir = '../../submissions/';

# Create CGI object
my $cgi = CGI->new;

# Read cookies (if any)
my %cookies       = CGI::Cookie->fetch;
my $cookie_name   = $cookies{Name}   ? $cookies{Name}->value   : '';
my $cookie_klasse = $cookies{Klasse} ? $cookies{Klasse}->value : '';
my $cookie_uuid   = $cookies{UUID} ? $cookies{UUID}->value : '';

# Get Data
my $name    = $cgi->param('Name')    // $cookie_name;
my $klasse  = $cgi->param('Klasse')  // $cookie_klasse;
my $aufgabe = $cgi->param('Aufgabe') // '';
my $link    = $cgi->param('Link')    // '';
my $uuid    = $cgi->param('UUID')    // $cookie_uuid;

#keep only name proportion of email - match all until first occurence of @
if ($name =~ m/@/) {
  $name =~ m/(.+?)@.*/;
  $name = $1;
}

# Sanitize name: keep letters, numbers, some signs
$name  =~ s/[^a-zA-Z0-9\-\.\_]//g;
$klasse  =~ s/[^a-zA-Z0-9]//g;
$aufgabe  =~ s/[^a-zA-Z0-9\-\.\_]//g;

# Sanitize name: keep all needed in URL https://webtigerpython.ethz.ch/#?code=
# and Base64URL encoding plus letters, numbers, dot, - _ # ? : /
$link    =~ s/[^a-zA-Z0-9\.\-\#_\?\:\=\/]//g;

# If the form was submitted via POST and we got all information we need - process request
if ($cgi->request_method eq 'POST' 
	&& $name ne "" && $name =~ /\w+/ 
	&& $klasse ne "" && $aufgabe =~ /\w|\d/ 
	&& $aufgabe ne "" && $klasse =~ /^\w\d\w$/ 
	&& $link ne "" && $link =~ m#^https://webtigerpython.ethz.ch/.+code.+#
) {
    # statistics
	my $utc_timestamp = time;
	my $IP = $ENV{"REMOTE_ADDR"};
	my $UA = $ENV{"HTTP_USER_AGENT"};
	
	if ($uuid eq '' || $uuid =~ /([^a-zA-Z0-9\-])/) {
	  $uuid = do { open my $fh, "/proc/sys/kernel/random/uuid" or die $!; scalar <$fh> };
	}
	# needed untainting in order to use T switch in shebang
	$uuid =~ /([a-zA-Z0-9\-]+)/;
	$uuid = $1;

    # Write to file
	my $fname = $uuid . '_' . $utc_timestamp . '.txt';
	my $outfile = $basedir . $fname;

	# content
	my $output = "'$IP','$UA','$klasse','$aufgabe','$name','$link'\n";

	# never overwrite files
	die "file $outfile exists - please try again" if -e $outfile;
	
	# create output file - just in case we have a collision we use >>
    open my $fh, '>>', $outfile or die "Cannot open $outfile: $!";
    print $fh $output;
    close $fh or die "Cannot close $outfile: $!";

	# Create cookies
    my $name_cookie = $cgi->cookie(
        -name  => 'Name',
        -value => $name,
        -expires => '+3h'
    );

    my $klasse_cookie = $cgi->cookie(
        -name  => 'Klasse',
        -value => $klasse,
        -expires => '+3h'
    );

    my $uuid_cookie = $cgi->cookie(
        -name  => 'UUID',
        -value => $uuid,
        -expires => '+1y'
    );
 	
	# Confirmation page
    print $cgi->header(
        -type   => 'text/html; charset=UTF-8',
        -cookie => [$name_cookie, $klasse_cookie, $uuid_cookie]
    );

print <<'HTML';
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Submitted</title>
	<meta http-equiv="refresh" content="2; url=submission.cgi">
</head>
<body>
    <h1 style="background-color:MediumSeaGreen;">Submission successful</h1>
    <p>Your WebTigerPython Link has been saved.<p>
HTML

print('<p><small>' . localtime($utc_timestamp) . '</small></p><p><small>' 
                   . $uuid . '</small></p><p><small>' 
				   . $link .'</small></p>');

print <<'HTML';
    <p><a href="submission.cgi">Submit another code link</a></p>
</body>
</html>
HTML
}
elsif ($cgi->request_method eq 'POST') {
    print $cgi->header('text/html; charset=UTF-8');
    print <<'HTML';
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>NOT Submitted</title>
	<meta http-equiv="refresh" content="5; url=submission.cgi">
</head>
<body>
    <h1 style="background-color:Tomato;">Submission FAILED</h1>
    <p>Your WebTigerPython Link has NOT been saved.</p>
    <p>Did you use a WRONG format for <b>Name</b> or <b>Klasse</b> or <b>Aufgabe</b> or <b>Link</b>?</p>
HTML
print("<p>Name: $name</p>");
print("<p>Klasse: $klasse</p>");
print("<p>Aufgabe: $aufgabe</p>");
print("<p>Link: $link</p>");
print("<p>UUID: $uuid</p>");
print <<'HTML';
    <p><a href="submission.cgi">Submit another code link</a></p>
</body>
</html>
HTML
}
else {
    # Show the form (GET request)
    print $cgi->header('text/html; charset=UTF-8');
    print <<'HTML';
<!DOCTYPE html>
<html lang="de">
  <head>
    <meta charset="UTF-8">
    <title>Submission Form</title>
  <style>
        body {
            font-family: sans-serif;
            max-width: 600px;
            margin: 2em auto;
        }
        label {
            display: block;
            margin-top: 1em;
        }
        div {
            display: block;
            margin-top: 1em;
			font-size: 0.5em;
        }
        input, textarea, button {
            width: 100%;
            padding: 0.5em;
            margin-top: 0.3em;
        }
        button {
			margin-top: 1.5em;
			background-color: #d32f2f;   /* red */
			color: white;
			border: none;
			border-radius: 4px;
			font-size: 1em;
			cursor: pointer;
    	}
    	button:hover {
        	background-color: #b71c1c;   /* darker red */
    	}
    </style>
  </head>
<body>

<h1>Submit a WebTigerPython Code Link</h1>

<form method="post" action="submission.cgi">
    <label title="YOUR.NAME@domain.tld"> 
HTML

if ($cookie_name ne '') {
  print($cookie_name)
} else {
  print('Name <input type="text" name="Name" required>')
}

print <<'HTML';
    </label>
    <label>
HTML

if ($cookie_klasse ne '') {
  print($cookie_klasse)
} else {
print <<'HTML';
        Klasse
		<select name="Klasse" id="Klasse" required>
		  <option label=" "></option>
		  <optgroup label="FMS">
			  <option value="F1A">F1A</option>
			  <option value="F1B">F1B</option>
			  <option value="F2A">F2A</option>
			  <option value="F2B">F2B</option>
			  <option value="F3A">F3A</option>
			  <option value="F3B">F3B</option>
		   </optgroup>
			  <optgroup label="GYM">
			  <option value="G1A">G1A</option>
			  <option value="G1B">G1B</option>
			  <option value="G1C">G1C</option>
			  <option value="G1D">G1D</option>
			  <option value="G1E">G1E</option>
			  <option value="G2A">G2A</option>
			  <option value="G2B">G2B</option>
			  <option value="G2C">G2C</option>
			  <option value="G2D">G2D</option>
			  <option value="G2E">G2E</option>
			  <option value="G3A">G3A</option>
			  <option value="G3B">G3B</option>
			  <option value="G3C">G3C</option>
			  <option value="G3D">G3D</option>
			  <option value="G3E">G3E</option>
			  <option value="G4A">G4A</option>
			  <option value="G4B">G4B</option>
			  <option value="G4C">G4C</option>
			  <option value="G4D">G4D</option>
			  <option value="G4E">G4E</option>
			</optgroup>
		</select>
HTML
}

print <<'HTML';
    </label>

    <label title="bspw. 1a oder 5g">
        Aufgabe
        <input type="text" name="Aufgabe" required>
    </label>

    <label title="https://webtigerpython.ethz.ch/#?code=...">
        WebTigerPython Code Link
        <textarea name="Link" rows="3" required></textarea>
    </label>

    <button type="submit">Create new submission</button>
</form>
HTML

if ($uuid ne '') {
print <<'HTML';
    <div>
        Unique Submission ID
HTML
print($uuid);
print <<'HTML';
    </div>
HTML
}

print <<'HTML';

</body>
</html>
HTML
}
