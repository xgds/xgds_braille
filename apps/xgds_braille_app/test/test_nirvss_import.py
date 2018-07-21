# __BEGIN_LICENSE__
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

import datetime
import json
import pytz

from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.core.urlresolvers import reverse
import couchdb
import time
import sys

from xgds_braille_app.models import NirvssSpectrometerDataProduct, NirvssSpectrometerSample
from xgds_braille_app.importer.importNirvssSpectra import importNirvssSpectra
from xgds_braille_app.importer.importDocImage import get_doc_metadata


class testNirvssSpectraImport(TestCase):
    """
    Tests the NIRVSS spectrometer CSV file importer
    """
    fixtures=['initial_data.json']

    def test_Import(self):
        num_sw_records = importNirvssSpectra('apps/xgds_braille_app/test/NIRVSS_SW_test.csv')
        num_lw_records = importNirvssSpectra('apps/xgds_braille_app/test/NIRVSS_LW_test.csv')
        # those test files contain 100 records each, make sure that many records were imported:
        assert(num_sw_records==100)
        assert(num_lw_records==100)
        # Now get one data product and check to make sure it contains 100 (wavelength,reflectance) pairs:
        nsdp = NirvssSpectrometerDataProduct.objects.all()[0]
        assert(nsdp.instrument is not None)
        assert(len(nsdp.samples)==100)
        for sample in nsdp.samples:
            assert(sample[0] is not None)
            assert(sample[1] is not None)
        # test the unicode method for a data product
        assert(len('%s'%nsdp)>0)
        # get samples from a data product
        samples = NirvssSpectrometerSample.objects.filter(dataProduct=nsdp)
        assert(len(samples)>0)
        # test unicode method for a sample
        assert(len('%s'%samples[0])>0)

    def test_classMethods(self):
        nsdp = NirvssSpectrometerDataProduct()
        assert(len(nsdp.getSearchableFields())>0)
        assert(len(nsdp.getSearchFormFields())>0)
        assert(len(nsdp.getSearchFieldOrder())>0)
        assert(nsdp.getDataForm('NIRVSS SW') is None)

class testDocImport(TransactionTestCase):
    fixtures=['initial_data.json','test_data.json']

    # This setup method is called before all tests in the class, and here we will use it to set up a separate
    # couchdb database, similar to the django test database, that we can modify during tests and delete later
    def setUp(self):
        self.test_db_name = 'test_xgds_braille_couchdb'
        settings.COUCHDB_FILESTORE_NAME = self.test_db_name
        self.couchdb_server = couchdb.server(settings.COUCHDB_URL)
        # if tests didn't end cleanly the old one could still be around; trying to create one will cause an error
        if self.test_db_name in self.couchdb_server:
            del self.couchdb_server[self.test_db_name]
        self.couchdb = self.couchdb_server.create(self.test_db_name)

    # This tear down method is called after all tests in the class, and here we will use it to delete the couchdb
    # test database, but we have to wait until the deepzoom image tiling thread is done, which we do by watching
    # a semaphore in the couchdb database
    def tearDown(self):
        print '\nWaiting for deepzoom thread to finish before tear down ',
        while self.couchdb['create_deepzoom_thread']['active'] == True:
            sys.stdout.write('|')
            sys.stdout.flush()
            time.sleep(1)
        print ' Done. Deleting couchdb test instance'
        del self.couchdb_server[self.test_db_name]

    def test_importDocImage(self):
        filename = 'apps/xgds_braille_app/test/my_interesting_doc_image_scale2.png'
        fp = open(filename)
        extras = get_doc_metadata(filename)
        url = reverse('xgds_save_image')
        data ={
            'timezone':'utc',
            'vehicle':'',
            'username':'root',
            'file':fp,
            'exif':extras
        }
        r = self.client.post(url, data=data)
        assert(r.status_code==200)
