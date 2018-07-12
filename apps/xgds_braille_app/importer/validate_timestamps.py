#!/usr/bin/env python
#  __BEGIN_LICENSE__
# Copyright (c) 2015, United States Government, as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All rights reserved.
#
# The xGDS platform is licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
# __END_LICENSE__

"""
Utilities for discovering telemetry files and launching the corresponding loader.
See ../../docs/dataImportYml.rst
"""


import yaml
import os
import re
import datetime
import pytz
from subprocess import Popen, PIPE
from threading import Timer
import shlex
import traceback
from dateutil.parser import parse as dateparser


class TimestampValidator:
    def __init__(self, config_yaml_path):
        # config comes from a YAML file
        self.config = yaml.load(open(config_yaml_path))
        self.registry = self.config['registry']
        # Local copy of processed files, which are also tracked in the database
        # in order to keep state when the import finder is restarted and for
        # reporting import status to users
        self.processed_files = []
        self.files_to_process = []
        # Keep track of the disposition of all discovered files:
        self.ignored_files = [] # matched an explicit ignore rule
        self.ambiguous_files = [] # matched more than one config rule
        self.unmatched_files = [] # matched no config rule
        self.timestamps_that_failed = [] # tried to import and failed
        self.timestamps_that_succeeded = [] # tried and succeeded
        # The actual timestamps
        self.timestamps = []

    def find_files(self,root_dir):
        for dirName, subdirList, fileList in os.walk(root_dir):
            #print('Found directory: %s' % dirName)
            for basename in fileList:
                filename = os.path.join(dirName, basename)

                # Identify which importer to use, and make sure it's a unique match
                matches = []
                for r in self.registry:
                    #print r['filepath_pattern']
                    match = re.search(r['filepath_pattern'], filename)
                    if match:
                        matches.append(r)
                if 1 == len(matches):
                    if 'ignore' in matches[0] and matches[0]['ignore']:
                        # matched an explicit ignore rule
                        print 'Ignoring', basename
                        self.ignored_files.append(filename)
                        continue
                    print 'Adding', basename
                    # unique match, add to the list of things to import
                    self.files_to_process.append((filename,matches[0]))
                elif 0 == len(matches):
                    print 'Warning: file %s does not match any importer config' % filename
                    self.unmatched_files.append(filename)
                else:
                    print 'Warning: file %s matches more than one importer config' % filename
                    for m in matches:
                        print m
                    self.ambiguous_files.append(filename)

        print 'Identified files to process:'
        for item in self.files_to_process:
            filename = item[0]
            registry = item[1]
            print '%s' % (filename)

    def process_files(self, username=None, password=None):
        for pair in self.files_to_process:
            filename, registry = pair
            arguments = ''
            if 'arguments' in registry:
                if '%(filename)s' in registry['arguments']:
                    arguments = registry['arguments']
                    arguments = arguments % {'filename': filename}
                else:
                    arguments = ' '.join([registry['arguments'], filename])
            else:
                arguments = filename

            if 'timestamp_extractor' in registry:
                cmd = ' '.join([registry['timestamp_extractor'], arguments])
                try:
                    proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
                except Exception as e:
                    print cmd
                    print str(e)
                    print traceback.format_exc()
                    continue
                timeout = 100
                timer = Timer(timeout, proc.kill)
                try:
                    timer.start()
                    (stdout, stderr) = proc.communicate()
                finally:
                    timer.cancel()

                # Keep track of successes and failures
                if proc.returncode == 0:
                    self.timestamps_that_succeeded.append(filename)
                else:
                    self.timestamps_that_failed.append(filename)

                # Aggregate outputs
                for line in stdout.splitlines():
                    #print line
                    try:
                        timestamp = dateparser(line)
                        if timestamp is not None:
                            self.timestamps.append(timestamp)
                    except ValueError:
                        # If the line does not parse as a timestamp it's probably some other stdout we can ignore
                        print 'Cannot parse time from "%s"' % line

                if stderr:
                    print cmd
                    print "stderr:"
                    print stderr,

    def print_stats(self):
        print 'Found %d files configured to ignore' % len(self.ignored_files)
        print 'Found %d ambiguous files, matched more than one config rule' % len(self.ambiguous_files)
        print 'Found %d unmatched files, matched no config rule' % len(self.unmatched_files)
        if len(self.files_to_process)>0:
            print 'Found %d files to process' % len(self.files_to_process)
        print 'Tried %d timestamps that failed' % len(self.timestamps_that_failed)
        print 'Tried %d timestamps that succeeded' % len(self.timestamps_that_succeeded)


def get_timestamp_from_dirname(dirname):
    pattern = '(\d{16})_(SCIENCE|SCOUTING)_(\d{2})'
    match = re.search(pattern,dirname)
    if match:
        timestamp = datetime.datetime.utcfromtimestamp(1e-6*int(match.group(1))).replace(tzinfo=pytz.utc)
        return timestamp
    return None


if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser('usage: %prog')
    parser.add_option('-c', '--configfile',
                      help='yaml config file for getting timestamps from files')
    parser.add_option('-t', '--test',
                      action='store_true', default=False,
                      help='Run in test mode')
    parser.add_option('-f', '--force',
                      action='store_true', default=False,
                      help='Force creation of a flight even if invalid timestamps are found')
    parser.add_option('-m', '--make_flight',
                      action='store_true', default=False,
                      help='Create a flight for the given directory')

    opts, args = parser.parse_args()

    # Get timestamp from root directory
    flight_dir = args[0]
    flight_dir_timestamp = get_timestamp_from_dirname(flight_dir)
    if flight_dir_timestamp is None:
        raise ValueError('Cannot get a valid timestamp from source root %s' % flight_dir)

    print 'Flight dir timestamp is %s' % flight_dir_timestamp

    # If we were given a timestamp validation config, go validate timestamps
    if opts.configfile is not None:
        validator = TimestampValidator(opts.configfile)
        validator.find_files(flight_dir)
        if not opts.test:
            validator.process_files()
        validator.print_stats()
        start_time = flight_dir_timestamp
        earliest_time = min(validator.timestamps)
        end_time = max(validator.timestamps)
        print 'start time:   ', start_time
        print 'earliest time:', earliest_time
        print 'end time:     ', end_time

        # If we were asked to create a flight, create it
        if opts.make_flight:
            try:
                # get or create a flight for that source root directory
                import django
                django.setup()
                from django.conf import settings
                from xgds_core.flightUtils import get_or_create_flight_with_source_root
                flight = get_or_create_flight_with_source_root(flight_dir,start_time,end_time)
                print 'Created or got flight %s' % flight
            except ImportError:
                print 'No django, cannot create a flight'
