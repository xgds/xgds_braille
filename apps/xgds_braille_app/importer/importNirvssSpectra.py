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

import optparse

import django
django.setup()
from django.conf import settings
from xgds_braille_app.models import NirvssSpectrometerDataProduct, NirvssSpectrometerSample, ScienceInstrument
from xgds_core.flightUtils import getFlight
from geocamTrack.utils import getClosestPosition

from csv import DictReader
import sys
import re
import datetime
from dateutil.parser import parse as dateparser
import pytz

from convertNirvssSpectra import create_band_depth_time_series
from createBandDepthGeoJSON import create_geojson_for_all_bdd


def importNirvssSpectra(filename):
    """
    Import NIRVSS spectra from a CSV file and write them to the database
    :param filename: the name of the CSV file
    :return: the number of spectra imported
    """
    num_imported = 0
    num_rejected_noflight = 0
    num_rejected_exists = 0

    # The only current way to know which instrument this is from is the filename
    if 'LW' in filename:
        instrumentName = 'NIRVSS LW'
    elif 'SW' in filename:
        instrumentName = 'NIRVSS SW'
    instrument = ScienceInstrument.getInstrument(instrumentName)

    # Use this to store objects and bulk create in groups
    queue = []

    reader = DictReader(open(filename,'r'))
    for row in reader:
        epochTime = datetime.datetime.utcfromtimestamp(float(row['Epoch Time'])).replace(tzinfo=pytz.UTC)

        flight = getFlight(epochTime, None)
        if flight is None:
            num_rejected_noflight += 1
            if num_rejected_noflight < 10:
                print 'No flight for', row
            continue

        # Check for existing database entries with this same instrument and acquisition time
        existingRecords = NirvssSpectrometerDataProduct.objects.filter(
                acquisition_time=epochTime,instrument=instrument
            )
        if len(existingRecords)>0:
            num_rejected_exists += 1
            if num_rejected_exists < 10:
                print 'This spectrum is already imported as:'
                for record in existingRecords:
                    print '    %s' % record
            continue

        track_position = None
        if flight:
            track_position = getClosestPosition(epochTime)

        # No existing records, so add this one
        nsdp = NirvssSpectrometerDataProduct()
        nsdp.description = ''
        nsdp.manufacturer_data_file = None
        nsdp.manufacturer_mime_type = 'text/plain'
        nsdp.portable_data_file = None
        nsdp.portable_mime_type = 'text/plain'
        nsdp.portable_file_format_name = 'ASCII'
        nsdp.acquisition_time = epochTime
        nsdp.acquisition_timezone = 'UTC'
        nsdp.creation_time = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        nsdp.track_position = track_position
        nsdp.user_position = None
        nsdp.collector = None
        nsdp.creator = None
        nsdp.instrument = instrument
        nsdp.name = nsdp.__unicode__()
        nsdp.flight = flight
        nsdp.save()
        num_imported += 1

        # Add all of the (wavelength,reflectance) values for the spectrum
        for column_label,value in row.iteritems():
            # NIRVSS csv header has channel names like "R2311", "R2323",
            # etc. which indicate wavelength, and the data rows contain
            # float values which are the radiance values
            match = re.search('R(\d+)',column_label)
            if match:
                # If the column header is R#### store the corresponding
                # radiance values as samples
                datapoint = NirvssSpectrometerSample()
                datapoint.dataProduct = nsdp
                datapoint.wavelength = int(match.group(1))
                datapoint.reflectance = float(value)
                queue.append(datapoint)
        NirvssSpectrometerSample.objects.bulk_create(queue)
        queue = []

    if flight is not None:
        # for this flight, create one band depth time series for all existing band depth definitions
        create_band_depth_time_series(flight=flight)

        # from each generated band depth time series, create a band depth geojson
        create_geojson_for_all_bdd(flight=flight)

    stats = {'num_imported': num_imported,
             'num_rejected_noflight': num_rejected_noflight,
             'num_rejected_exists': num_rejected_exists}
    return stats

if __name__=='__main__':
    # TODO: reconcile whether we get the instrument from a command line arg or infer from the filename
    parser = optparse.OptionParser('usage: %prog')
    parser.add_option('-i', '--instrument', help='instrument that was the source of this file')

    nirvssFilename = sys.argv[1]
    start_time = datetime.datetime.now()
    import_stats = importNirvssSpectra(nirvssFilename)
    end_time = datetime.datetime.now()
    print 'Import took %s' % (end_time-start_time)
    print 'Imported %d ' % import_stats['num_imported']
    print 'Rejected %d because no flight matches' % import_stats['num_rejected_noflight']
    print 'Rejected %d that were already imported' % import_stats['num_rejected_exists']
