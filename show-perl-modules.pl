#!/usr/bin/perl -w
use strict;
use warnings;
use CGI qw(:standard);

# Create CGI object
my $cgi = CGI->new;
print $cgi->header('text/html; charset=UTF-8');

# import utility libraries
use CGI::Cookie;
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use File::Find;

print <<'HTML';
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>show</title>
	<link rel="stylesheet" href="https://rocco.melzian.ch/css/style.css">
</head>
<body>
    <h1 style="background-color:MediumSeaGreen;">Available Modules</h1>
HTML

my @files;

find(
  {
    wanted => sub { push @files, $File::Find::fullname if -f $File::Find::fullname && /\.pm$/ },
    follow => 1,
    follow_skip => 2,
  },
  @INC
);

for my $file (sort @files) {

	my $document = do {
		local $/ = undef;
		open my $fh, "<", $file
			or die "could not open $file: $!";
		<$fh>;
	};
	print '<div class="tooltip">' . $file . '<span class="tooltiptext">cat ' .  $file . '</span></div><br>';
}

print <<'HTML';
</body>
</html>
HTML
