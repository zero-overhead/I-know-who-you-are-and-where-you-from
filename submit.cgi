#!/usr/bin/perl -wT
use strict;
use warnings;
use CGI qw(:standard);
#use CGI::Carp qw(warningsToBrowser fatalsToBrowser);

#where to store the output files
my $basedir = '../../submissions/';

# Create CGI object
my $cgi = CGI->new;
print $cgi->header('text/html; charset=UTF-8');

# Get Data
my $name = $cgi->param('Name') // '';
my $identifier = $cgi->param('Identifier') // '';
my $aufgabe = $cgi->param('Aufgabe') // '';
my $link = $cgi->param('Link') // '';

# Sanitize name: keep letters
$name  =~ s/[^a-zA-Z0-9\s\-]//g;
$name  =~ s/\s/_/g;
$identifier  =~ s/[^a-z]//g;
$aufgabe  =~ s/[^a-zA-Z0-9\-\.\_]//g;

# Sanitize name: keep all needed in URL https://webtigerpython.ethz.ch/#?code=
# and Base64URL encoding plus letters, numbers, dot, - _ # ? : /
$link    =~ s/[^a-zA-Z0-9\.\-\#_\?\:\=\/]//g;

# If the form was submitted via POST and we got all information we need - process request
if ($cgi->request_method eq 'POST' 
	&& $name ne "" && $name =~ /\w/ 
	&& $identifier ne "" && $identifier =~ /^\w\w\w\w\w\w$/ 
	&& $aufgabe ne "" 
	&& $link ne "" && $link =~ m#^https://webtigerpython.ethz.ch/.+code.+#
) {
    # statistics
	my $utc_timestamp = time;
	my $IP = $ENV{"REMOTE_ADDR"};
	my $UA = $ENV{"HTTP_USER_AGENT"};
	
	# needed untainting in order to use T switch in shebang
	$identifier =~ /([a-z]+)/;
	$identifier = $1;

	$name =~ /([a-zA-Z0-9\-]+)/;
	$name = $1;

	$aufgabe =~ /([a-zA-Z0-9\-\.\_]+)/;
	$aufgabe = $1;

	# Write to file
	my $fname = $identifier . '_' . $utc_timestamp . '_' . $name . '_' . $aufgabe . '.txt';
	my $outfile = $basedir . $fname;

	# content
	my $output = "'$IP','$UA','$identifier','$name','$aufgabe','$link'\n";

	# never overwrite files
	die "file $outfile exists - please try again" if -e $outfile;
	
	# create output file - just in case we have a collision we use >>
    open my $fh, '>>', $outfile or die "Cannot open $outfile: $!";
    print $fh $output;
    close $fh or die "Cannot close $outfile: $!";
 	
	# Confirmation page
print <<'HTML';
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Submitted</title>
	<meta http-equiv="refresh" content="2; url=submit.cgi">
</head>
<body>
    <h1 style="background-color:MediumSeaGreen;">Submission successful</h1>
    <p>Your WebTigerPython Link has been saved.<p>
HTML

print('<p>Time: ' . localtime($utc_timestamp) . '</p>' .
	  '<p>Name: ' . $name . '</p>' . 
	  '<p>Aufgabe: ' . $aufgabe . '</p>' . 
	  '<p><small>Link: ' . $link .'</small></p>');

print <<'HTML';
    <p><a href="submission.cgi">Submit another code link</a></p>
</body>
</html>
HTML
}
elsif ($cgi->request_method eq 'POST') {
    print <<'HTML';
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>NOT Submitted</title>
	<meta http-equiv="refresh" content="5; url=submit.cgi">
</head>
<body>
    <h1 style="background-color:Tomato;">Submission FAILED</h1>
    <p>Your WebTigerPython Link has NOT been saved.</p>
    <p>Did you use a WRONG format for  <b>Name</b> or <b>Aufgabe</b> or <b>Identifier</b> or <b>Link</b>?</p>
HTML
print("<p>Identifier: $identifier</p>");
print("<p>Link: $link</p>");
print <<'HTML';
    <p><a href="submit.cgi">Submit another code link</a></p>
</body>
</html>
HTML
}
else {
    # Show the form (GET request)
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

<h1>Submit a WebTigerPython Code Link</h1>

<form method="post" action="submit.cgi">
    <label title="Dein Name - bspw. 'Susi S.'"> 
	  Name <input type="text" name="Name" minlength="2" maxlength="25" required>
	</label>
    <label title="Dein Passwort aus 6 Kleinbuchstaben - bspw. 'agewha' oder 'xsdfed'"> 
	  Password <input type="text" name="Identifier" minlength="6" maxlength="6" required>
	</label>
    <label title="Die Aufgabennummer - bspw. '1a' oder '3b'"> 
	  Aufgabe <input type="text" name="Aufgabe" minlength="1" maxlength="4" required>
	</label>
    <label title="https://webtigerpython.ethz.ch/#?code=...">
        WebTigerPython Code Link
        <textarea name="Link" rows="3" required></textarea>
    </label>
    <button type="submit">Create new submission</button>
</form>
</body>
</html>
HTML
}
