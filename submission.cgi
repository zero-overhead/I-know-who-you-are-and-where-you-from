#!/usr/bin/perl -w
use strict;
use warnings;
use CGI qw(:standard);
use CGI::Cookie;
#use CGI::Carp qw(warningsToBrowser fatalsToBrowser);

#where to store the output files
my $basedir = '/home/httpd/vhosts/melzian.ch/submissions/';

# Create CGI object
my $cgi = CGI->new;

# Read cookies (if any)
my %cookies = CGI::Cookie->fetch;
my $cookie_name   = $cookies{Name}   ? $cookies{Name}->value   : '';
my $cookie_klasse = $cookies{Klasse} ? $cookies{Klasse}->value : '';

# Get Data
my $name    = $cgi->param('Name')    // '';
my $klasse  = $cgi->param('Klasse')  // '';
my $aufgabe = $cgi->param('Aufgabe') // '';
my $link    = $cgi->param('Link')    // '';

# Sanitize name: keep letters, numbers
$name    =~ s/[^a-zA-Z0-9]//g;
$klasse  =~ s/[^a-zA-Z0-9]//g;
$aufgabe =~ s/[^a-zA-Z0-9]//g;
# Sanitize name: keep all needed in URL https://webtigerpython.ethz.ch/#?code=
# and Base64URL encoding plus letters, numbers, dot, - _ # ? : /
$link    =~ s/[^a-zA-Z0-9\.\-\#_\?\:\=\/]//g;

# If the form was submitted via POST
if ($cgi->request_method eq 'POST' && $name ne "" &&  $klasse ne "" &&  $klasse =~ /^\w\d\w$/ &&  $aufgabe ne "" &&  $link ne "" && $link =~ m#^https://webtigerpython.ethz.ch/.*\?code=.+# ) {

    # statistics
	my $utc_timestamp = time;
	my $IP = $ENV{"REMOTE_ADDR"};
	my $UA = $ENV{"HTTP_USER_AGENT"};

    # Write to file
	my $fname = $utc_timestamp . '_' . $klasse . '_' . $name . '_' . $aufgabe . '.txt';
	my $outfile = $basedir . $fname;

	my $output = "$utc_timestamp,$IP,'$UA','$name','$klasse','$aufgabe','$link'\n";

    open my $fh, '>>', $outfile or die "Cannot open $outfile: $!";
    print $fh $output;
    close $fh or die "Cannot close $outfile: $!";

	# Create cookies
    my $name_cookie = $cgi->cookie(
        -name  => 'Name',
        -value => $name,
        -expires => '+2h'
    );

    my $klasse_cookie = $cgi->cookie(
        -name  => 'Klasse',
        -value => $klasse,
        -expires => '+2h'
    );

	# Confirmation page
    print $cgi->header(
        -type   => 'text/html; charset=UTF-8',
        -cookie => [$name_cookie, $klasse_cookie]
    );

    print <<'HTML';
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Submitted</title>
	<meta http-equiv="refresh" content="2; url=submission.cgi" />
</head>
<body>
    <h1>Submission successful</h1>
    <p>Your data has been saved.</p>
    <p><a href="submission.cgi">Submit another code link</a></p>
</body>
</html>
HTML

}
elsif ($cgi->request_method eq 'POST' && $name ne "" &&  $klasse ne "" &&  $aufgabe ne "" &&  $link ne "") {
    print $cgi->header('text/html; charset=UTF-8');
    print <<'HTML';
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>NOT Submitted</title>
	<meta http-equiv="refresh" content="5; url=submission.cgi" />
</head>
<body>
    <h1>Submission FAILED</h1>
    <p>Your data has NOT been saved.</p>
    <p>Did you use a WRONG format for <b>Klasse</b> or <b>Link</b>?</p>
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

<h1>Submit WebTigerPython Code Link</h1>

<form method="post" action="submission.cgi">
    <label>
        Name
        <input type="text" name="Name" 
HTML

if($cookie_name ne '') {
  print('value="' . $cookie_name . '"')
}

    print <<'HTML';
  required>
    </label>

    <label>
        Klasse
        <input type="text" name="Klasse" 
HTML

if($cookie_klasse ne '') {
  print('value="' . $cookie_klasse . '"')
}

    print <<'HTML';
 required>
    </label>

    <label>
        Aufgabe
        <input type="text" name="Aufgabe" required>
    </label>

    <label>
        WebTigerPython Code Link
        <textarea name="Link" rows="3" required></textarea>
    </label>

    <button type="submit">Create new submission</button>
</form>
</body>
</html>
HTML
}
