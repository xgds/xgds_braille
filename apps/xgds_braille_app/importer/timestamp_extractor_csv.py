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
    reader = DictReader(open(filename,'r'), delimiter=options.delimiter)
    for row in reader:
        timestampString = row[options.column]
        if timestampString:
            if options.type == 'seconds':
                epochTime = datetime.datetime.utcfromtimestamp(float(timestampString)).replace(tzinfo=pytz.UTC)
            elif options.type == 'microseconds':
                epochTime = datetime.datetime.utcfromtimestamp(1e-6*int(timestampString)).replace(tzinfo=pytz.UTC)
            print epochTime
            num_imported += 1

    stats = {'num_imported': num_imported}
    return stats

if __name__=='__main__':
    # TODO: reconcile whether we get the instrument from a command line arg or infer from the filename
    parser = optparse.OptionParser('usage: %prog')
    parser.add_option( '-d', '--delimiter', default=',' )
    parser.add_option( '-c', '--column' )
    parser.add_option( '-t', '--type' )
    options, arguments = parser.parse_args()
    if options.delimiter == 'tab':
        options.delimiter = '\t'

    csvFilename = arguments[0]
    import_stats = parseTimestampsFromCSV(csvFilename, options)
    print 'Imported %d ' % import_stats['num_imported']
