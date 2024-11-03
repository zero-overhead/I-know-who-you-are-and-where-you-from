#!/usr/bin/perl

print "Content-type: text/html\n\n";
print "<!DOCTYPE html><html lang='de'><head><title>Was ist meine IP?</title><style>table, th, td {border: 1px solid;}</style><meta charset='utf-8'/></head><body><table><tr><th>Variable</th><th>Wert</th></tr>";
foreach (sort keys %ENV) {
   print "<tr><td>$_</td><td>$ENV{$_}</td></tr>";
}
print "</table></body></html>";
