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
import time
import traceback


class TimestampFinder:
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

    def get_new_files(self):
        print self.config['import_path']
        for dirName, subdirList, fileList in os.walk(self.config['import_path']):
            print('Found directory: %s' % dirName)
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
                    print cmd
                    proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
                except Exception as e:
                    print str(e)
                    print traceback.format_exc()
                    continue
                timeout = 100
                timer = Timer(timeout, proc.kill)
                start_import_time = pytz.timezone('utc').localize(datetime.datetime.utcnow())
                try:
                    timer.start()
                    (stdout, stderr) = proc.communicate()
                finally:
                    timer.cancel()
                end_import_time = pytz.timezone('utc').localize(datetime.datetime.utcnow())

                # If it succeeded, keep track that we did this one
                if proc.returncode == 0:
                    self.timestamps_that_succeeded.append(filename)
                else:
                    self.timestamps_that_failed.append(filename)
                print "stdout:", stdout
                print "stderr:", stderr

    def print_import_stats(self):
        print 'Found %d files configured to ignore' % len(self.ignored_files)
        print 'Found %d ambiguous files, matched more than one config rule' % len(self.ambiguous_files)
        print 'Found %d unmatched files, matched no config rule' % len(self.unmatched_files)
        if len(self.files_to_process)>0:
            print 'Found %d files to process' % len(self.files_to_process)
        print 'Tried %d timestamps that failed' % len(self.timestamps_that_failed)
        print 'Tried %d timestamps that succeeded' % len(self.timestamps_that_succeeded)

if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser('usage: %prog')
    parser.add_option('-t', '--test',
                      action='store_true', default=False,
                      help='Run in test mode: find files and report them but do not process them')
 
    opts, args = parser.parse_args()

    finder = TimestampFinder(args[0])
    finder.get_new_files()
    if not opts.test:
        finder.process_files()
    finder.print_import_stats()
