#!/usr/bin/perl -w
use strict;
use warnings;
use CGI qw(:standard);
use CGI::Cookie;
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use File::Find;
#use Data::Dumper;

# Create CGI object
my $cgi = CGI->new;
print $cgi->header('text/html; charset=UTF-8');

my $folder = $cgi->param('folder');
# needed untainting in order to use T switch in shebang
$folder =~ /([a-z]+)/;
$folder = $1;
	
unless ($folder eq 'exam' || $folder eq 'trunk' || $folder eq 'exercise') {
  $folder = 'exercise'
}

#where to read the submission files
my $basedir = '../../submissions/' . $folder;

print <<'HTML';
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>WebTigerPython Code Link Checker</title>
	<link rel="stylesheet" href="../css/style.css">
</head>
<body>
    <h1 style="background-color:MediumSeaGreen;">
HTML
print $basedir;
print "</h1>";

my @files;
find(
      { wanted => sub {
                push @files, $File::Find::fullname
                if -f $File::Find::fullname && /\.txt$/
        },
        follow => 1,
        follow_skip => 2,
      },
      $basedir
);

my %submissions;

for my $file (sort @files) {
	#gokbim_1767622546_Betl_1.txt
	#0fae5512-41f9-4edf-b68c-71d21cfb04b3_1767790934.txt
	my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$submission_time,$blksize,$blocks) = stat($file) or die "Cannot stat $file: $!";

    my $document = do {
		local $/ = undef;
		open my $fh, "<", $file
			or die "could not open $file: $!";
		<$fh>;
	};
	#'46.245.151.226','Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.139 SEB/3.10.0 (x64) EXAM_#THISISNOTVERYSECRET#_NET_POPUPS_EXT_RESOURCES_INSIDE_SEB_SERVER','gokbim','Betl','1','https://webtigerpython.ethz.ch/#?code=NobwRAdghgtgpmAXGGUCWEB0AHAnmAGjABMoAXKJMAMwCcB7GAAgHMyBXWsgGzibRjZ6XJgCoAOhFQBrOABVOPOAAoAlJMnVhTafwhNaUCCxUA2VYklNrTLbX56DRk02UBmC1Zve7Adyi0xMoAHAAM6vreNrRoLAAWZO6moQD0Hl7WvNSJbskp5hlMYAC-ALpAA'

	# Remove newlines and split on ',' surrounded by quotes
	my @fields = split /','/, $document;
	s/^'|'$//g for @fields;   # remove leading/trailing quotes

	my %submission = (
		file      => $file,
		ts        => $submission_time,
		ip        => $fields[0],
		useragent => $fields[1],
		password  => $fields[2],
		name      => $fields[3],
		question  => $fields[4],
		url       => $fields[5],
	);
	my $uuid = $submission{ts} . '_' . $submission{password} . '_' . $submission{name}  . '_' . $submission{question};
	$submissions{$uuid} = \%submission; 
}

print <<'HTML';
	<input type="text" id="search" placeholder="Search for anything...">
	<table id="searchTable">
	<thead>
	<tr><th>Zeit</th><th>Name</th><th>Identifier</th><th>Frage</th><th>IP</th><th>File</th><th>User Agent</th></tr>
	</thead>
	<tbody>
HTML

for my $submission (sort %submissions) {
	print '<tr><td>' . localtime($submissions{$submission}->{'ts'}) . '</td><td><a target="_blank" href="' . $submissions{$submission}->{'url'} . '">' . $submissions{$submission}->{'name'} . '</a></td><td>' . $submissions{$submission}->{'password'} . '</td><td>' . $submissions{$submission}->{'question'} . '</td><td>' . $submissions{$submission}->{'ip'} . '</td><td>' . $submissions{$submission}->{'file'} . '</td><td>'  . $submissions{$submission}->{'useragent'}  . '</td></tr>' if $submissions{$submission}->{'ts'};
}

print <<'HTML';
</tbody>
</table>
<script>
  const searchInput = document.getElementById('search');
  const table = document.getElementById('searchTable').getElementsByTagName('tbody')[0];

  searchInput.addEventListener('keyup', function() {
    const filter = this.value.toLowerCase();
    const rows = table.getElementsByTagName('tr');

    for (let row of rows) {
      let text = row.textContent.toLowerCase();
      row.classList.toggle('hidden', !text.includes(filter));
    }
  });
</script>
</body>
</html>
HTML
