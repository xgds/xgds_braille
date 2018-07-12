#!/usr/bin/env python

import optparse

from csv import DictReader
import sys
import re
import datetime
from dateutil.parser import parse as dateparser
import pytz

def parseTimestampsFromCSV(filename, options):
    num_imported = 0
    if options.column_number:
        column_number = int(options.column_number)
        fieldnames = ['%d'%n for n in range(column_number+1)]
        reader = DictReader(open(filename, 'r'), delimiter=options.delimiter,
                            fieldnames=fieldnames)
        options.column_name = options.column_number
    else:
        reader = DictReader(open(filename,'r'), delimiter=options.delimiter)

    for row in reader:
        timestampString = row[options.column_name]
        if timestampString:
            if options.type == 'seconds':
                epochTime = datetime.datetime.utcfromtimestamp(float(timestampString)).replace(tzinfo=pytz.UTC)
            elif options.type == 'microseconds':
                epochTime = datetime.datetime.utcfromtimestamp(1e-6*int(timestampString)).replace(tzinfo=pytz.UTC)
            elif options.type == 'iso8601':
                epochTime = dateparser(timestampString)
                #print 'timezone:', epochTime.tzname()

            print epochTime.isoformat()
            num_imported += 1

    stats = {'num_imported': num_imported}
    return stats

if __name__=='__main__':
    # TODO: reconcile whether we get the instrument from a command line arg or infer from the filename
    parser = optparse.OptionParser('usage: %prog')
    parser.add_option( '-d', '--delimiter', default=',' )
    parser.add_option( '-c', '--column_number' )
    parser.add_option( '-n', '--column_name' )
    parser.add_option( '-t', '--type' )
    options, arguments = parser.parse_args()
    if options.delimiter == 'tab':
        options.delimiter = '\t'

    csvFilename = arguments[0]
    import_stats = parseTimestampsFromCSV(csvFilename, options)
    print 'Found %d timestamps' % import_stats['num_imported']
