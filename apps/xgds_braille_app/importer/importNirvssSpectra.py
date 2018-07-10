#!/usr/bin/env python

import optparse

import django
django.setup()
from django.conf import settings
from xgds_braille_app.models import NirvssSpectrometerDataProduct, NirvssSpectrometerSample, ScienceInstrument
from xgds_core.flightUtils import get_or_create_flight
from csv import DictReader
import sys
import re
import datetime
from dateutil.parser import parse as dateparser
import pytz

from convertNirvssSpectra import create_band_depth_time_series
from createBandDepthGeoJSON import create_geojson_for_all_bdd


def fixTimezone(the_time):
    if not the_time.tzinfo or the_time.tzinfo.utcoffset(the_time) is None:
        the_time = pytz.timezone('utc').localize(the_time)
    the_time = the_time.astimezone(pytz.utc)
    return the_time


def importNirvssSpectra(filename):
    """
    Import NIRVSS spectra from a CSV file and write them to the database
    :param filename: the name of the CSV file
    :return: the number of spectra imported
    """
    num_imported = 0

    # The only current way to know which instrument this is from is the filename
    if 'LW' in filename:
        instrumentName = 'NIRVSS LW'
    elif 'SW' in filename:
        instrumentName = 'NIRVSS SW'
    instrument = ScienceInstrument.getInstrument(instrumentName)

    # Use this to store objects and bulk create in groups
    queue = []

    flight =  None

    reader = DictReader(open(filename,'r'))
    for row in reader:
        acqTime = fixTimezone(dateparser(row['Acquisition Time']))
        if not flight:
            flight = get_or_create_flight(acqTime)
        epochTime = fixTimezone(datetime.datetime.fromtimestamp(float(row['Epoch Time'])))

        # Check for existing database entries with this same instrument and acquisition time
        existingRecords = NirvssSpectrometerDataProduct.objects.filter(
                acquisition_time=epochTime,instrument=instrument
            )
        if len(existingRecords)>0:
            print 'This spectrum is already imported as:'
            for record in existingRecords:
                print '    %s' % record
            continue

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
        nsdp.creation_time = fixTimezone(datetime.datetime.utcnow())
        nsdp.track_position = None
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

    # for this flight, create one band depth time series for all existing band depth definitions
    create_band_depth_time_series(flight=flight)

    # from each generated band depth time series, create a band depth geojson
    create_geojson_for_all_bdd(flight=flight)

    return num_imported


if __name__=='__main__':
    parser = optparse.OptionParser('usage: %prog')
    parser.add_option('-i', '--instrument', help='instrument that was the source of this file')

    nirvssFilename = sys.argv[1]
    start_time = datetime.datetime.now()
    num_imported = importNirvssSpectra(nirvssFilename)
    end_time = datetime.datetime.now()
    print 'Import took %s' % (end_time-start_time)
    print 'Imported %d ' % num_imported
