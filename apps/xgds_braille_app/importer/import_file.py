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
URL_TAIL = '/genericFileUploadUrlDoesntExist/'

def fixTimezone(the_time):
    if not the_time.tzinfo or the_time.tzinfo.utcoffset(the_time) is None:
        the_time = pytz.timezone('utc').localize(the_time)
    the_time = the_time.astimezone(pytz.utc)
    return the_time


def import_file(filename):
    data ={
        'username':'root',
    }
    fp = open(filename)
    files = {'file': fp}

    # TODO: reverse is only getting the last part, missing '<http(s)>://<hostname>/'
    url = reverse('addTile')
    # ... so roll it like this:
    url = "%s://%s%s" % (HTTP_PREFIX, URL_PREFIX, URL_TAIL)

    r = requests.post(url, data=data, files=files, verify=False, auth=('root','xgds'))
    if r.status_code == 200:
        print 'HTTP status code:', r.status_code
        print r.text
        return 0
    else:
        sys.stderr.write('HTTP status code:', r.status_code, '\n')
        sys.stderr.write(r.text)
        sys.stderr.write('\n')
        sys.stderr.flush()
        return -1


if __name__=='__main__':
    import optparse
    parser = optparse.OptionParser('usage: %prog')
    opts, args = parser.parse_args()
    filename = arg[0]
    sys.stderr.write('Generic file import not yet supported\n')
    sys.exit(-1)
    retval = import_file(filename)
    sys.exit(retval)
