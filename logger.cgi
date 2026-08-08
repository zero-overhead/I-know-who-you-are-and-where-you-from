#!/usr/bin/perl -wT

use strict;
use warnings;
use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use JSON;
use POSIX qw(strftime);
use File::Path qw(make_path);

# we run e.g. this cron job to keep the folder clean
#
# Delete old or big data files & all empty folders
# STUDENT_DATA_DIR=rocco.melzian.ch/pub/students/data-logger && find $STUDENT_DATA_DIR -type f -mtime +30 -delete && find $STUDENT_DATA_DIR -type f -size +1M -delete && find $STUDENT_DATA_DIR -type d -empty -delete
my $base_dir = '../pub/students/data-logger';
my $max_file_size_in_byte = 1024 * 8;

my $time = time;
#my $local_string = strftime "%Y-%m-%d %H:%M:%S", localtime($time);
my $utc_string = strftime "%Y-%m-%d %H:%M:%S", gmtime($time);

# Create CGI object
my $cgi = CGI->new;

# Get all parameters
my %params = $cgi->Vars;

# Check for api_key
my $api_key = $params{'api_key'};

# Sanitize (basic) to pass Perl T argument
$api_key =~ /([a-zA-Z0-9_-]+)/;
$api_key = $1;

# Set response header
print $cgi->header('application/json');

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

# check maximum file size limit
my $filesize = -s $file;
if ($filesize > $max_file_size_in_byte) {
    unlink $file;
	print encode_json({ status => "error", message => "Too much data: $filesize while allowed max is only $max_file_size_in_byte"});
    exit;
}

# Response
print encode_json({
    status  => "success",
    #message	=> "Data stored",
    file	=> $file,
	size	=> $filesize 
});
