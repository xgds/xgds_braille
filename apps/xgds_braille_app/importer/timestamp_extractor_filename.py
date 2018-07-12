#!/usr/bin/env python

import optparse

from csv import DictReader
import sys
import re
import datetime
from dateutil.parser import parse as dateparser
import pytz

def parseTimestampsFromFilename(filename, options):
    num_imported = 0

    if options.type == 'seconds':
        timestamp_pattern = '(\d{10}\.\d{4,10})'
        match = re.search(timestamp_pattern,filename)
        if match:
            timestampString = match.groups()[-1]
            epochTime = datetime.datetime.utcfromtimestamp(float(timestampString)).replace(tzinfo=pytz.UTC)
        else:
            raise ValueError('Could not find expected time string in %s' % filename)

    elif options.type == 'microseconds':
        timestamp_pattern = '(\d{16})'
        match = re.search(timestamp_pattern, filename)
        if match:
            timestampString = match.groups()[-1]
            epochTime = datetime.datetime.utcfromtimestamp(1e-6*int(timestampString)).replace(tzinfo=pytz.UTC)
        else:
            raise ValueError('Could not find expected time string in %s' % filename)

    print epochTime.isoformat()
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

    filename = arguments[0]
    import_stats = parseTimestampsFromFilename(filename, options)
    print 'Found %d timestamps' % import_stats['num_imported']
