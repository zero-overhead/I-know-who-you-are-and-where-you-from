#!/usr/bin/perl

use strict;
use warnings;
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use JSON;
use POSIX qw(strftime);
use File::Path qw(make_path);

my $base_dir = '../pub/students/data-logger';

my $time = time;
#my $local_string = strftime "%Y-%m-%d %H:%M:%S", localtime($time);
my $utc_string = strftime "%Y-%m-%d %H:%M:%S", gmtime($time);

# Create CGI object
my $cgi = CGI->new;

# Set response header
print $cgi->header('application/json');

# Get all parameters
my %params = $cgi->Vars;

# Check for api_key
my $api_key = $params{'api_key'};
# Sanitize (basic)
$api_key =~ s/[^a-zA-Z0-9_\-]//g;

if (!$api_key) {
    print encode_json({ status => "error", message => "Missing or wrong api_key" });
    exit;
}

# Remove api_key from stored data if you don't want duplication
delete $params{'api_key'};

# Directory to store files
my $dir = "$base_dir/$api_key";
make_path($dir) unless -d $dir;

#$params{'local'} = $local_string;
$params{'utc'} = $utc_string;
my $file = "$dir/$time.json";

# Write JSON file
open(my $fh, '>', $file) or do {
    print encode_json({ status => "error", message => "Cannot write file" });
    exit;
};

print $fh encode_json(\%params);
close($fh);

# Response
print encode_json({
    status  => "success",
    message => "Data stored",
    file    => $file
});