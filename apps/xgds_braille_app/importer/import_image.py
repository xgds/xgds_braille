#!/usr/bin/env python

import django
django.setup()
from django.conf import settings
from django.core.urlresolvers import reverse

import sys
import re
import requests

import datetime
from dateutil.parser import parse as dateparser
import pytz
import json

HTTP_PREFIX = 'https'
URL_PREFIX = 'localhost'


def fixTimezone(the_time):
    if not the_time.tzinfo or the_time.tzinfo.utcoffset(the_time) is None:
        the_time = pytz.timezone('utc').localize(the_time)
    the_time = the_time.astimezone(pytz.utc)
    return the_time


def import_image(filename,camera):
    data ={
        'timezone':'utc',
        'vehicle':'',
        'username':'root',
        'camera': camera
    }
    fp = open(filename)
    files = {'file': fp}

    # TODO: reverse is only getting the last part, missing '<http(s)>://<hostname>/'
    url = reverse('xgds_save_image')
    # ... so roll it like this:
    url = "%s://%s%s" % (HTTP_PREFIX, URL_PREFIX, '/xgds_image/rest/saveImage/')

    r = requests.post(url, data=data, files=files, verify=False, auth=('root','xgds'))
    if r.status_code == 200:
        print 'HTTP status code:', r.status_code
        print r.text
        return 0
    else:
        sys.stderr.write('HTTP status code: %d\n' % r.status_code)
        sys.stderr.write(r.text)
        sys.stderr.write('\n')
        sys.stderr.flush()
        return -1


if __name__=='__main__':
    import optparse
    parser = optparse.OptionParser('usage: %prog')
    parser.add_option('-c', '--camera',
                      help='Name of the camera this image came from')
    opts, args = parser.parse_args()
    print opts.camera
    camera = opts.camera
    filename = args[0]
    retval = import_image(filename,camera=camera)
    sys.exit(retval)