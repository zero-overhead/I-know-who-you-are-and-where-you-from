#!/usr/bin/perl
#
# This script illustrates what a simple call to a website exposes about the user.
#
use strict;
use warnings;
use utf8;
use CGI;
use CGI::Cookie;
#use CGI::Carp 'fatalsToBrowser';
use JSON;
use LWP::Simple;
use POSIX qw(strftime);

my $ip = $ENV{"REMOTE_ADDR"};
my $timestamp = strftime "%a %b %e %H:%M:%S %Y", localtime;
my $random_value = int(rand(1000000));

my $cookie = CGI::Cookie->new(-name=>'ID', -value=>$random_value, -max-age=>'+1d', -secure=>0, -httponly=>0);
my $cgi = CGI->new();

print $cgi->header('text/html', -cookie => $cookie);
print $cgi->start_html(-title => 'IP: ' . $ip);

my $location_info = decode_json get("http://ip-api.com/json/$ip");
my $headers = {map { $_ => $cgi->http($_) } $cgi->http()};
my $cookies = {CGI::Cookie->fetch};

my %entries =  ( "Was deine IP Adresse $ip über dich verrät:" => $location_info,
	             'Informationen, die dein Browser preisgibt:' => $headers, 
    	         'Zum Schluss noch Cookies:' => $cookies
				 );
			   
for my $h ( sort keys %entries ) {
    my $entry = $entries{$h};
	print $cgi->h1($h);
	print "<table>";
	for my $k ( sort keys $entry ) {
		print "<tr><td>$k</td><td>$entry->{$k}</td></tr>";
	}
	print "</table>";
}

print $cgi->h1("Wo sind die Koordinaten $location_info->{'lat'} | $location_info->{'lon'} eigentlich?");
print "<iframe name='user_location' src='https://maps.google.com/maps?q=$location_info->{'lat'},$location_info->{'lon'}&amp;output=embed' width='640px' height='480px'></iframe>";

print "<hr />";

print '<p><a href="https://github.com/zero-overhead/I-know-who-you-are-and-where-you-from">client.pl source file</a> [ <a href="https://validator.w3.org/"><img src="https://www.w3.org/Icons/valid-xhtml10" alt="Valid XHTML 1.0 Transitional" height="31" width="88" /></a> | ' . $timestamp . '</p>';

print $cgi->end_html();
