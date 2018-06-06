#__BEGIN_LICENSE__
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
#__END_LICENSE__

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models

import xgds_timeseries.models as xgds_timeseries
from xgds_instrument.models import ScienceInstrument, AbstractInstrumentDataProduct
from xgds_notes2.models import NoteLinksMixin, NoteMixin, DEFAULT_NOTES_GENERIC_RELATION
from xgds_core.models import HasFlight, DEFAULT_FLIGHT_FIELD


class NirvssSpectrometerDataProduct(AbstractInstrumentDataProduct, NoteLinksMixin, NoteMixin, HasFlight):
        flight = DEFAULT_FLIGHT_FIELD()
        notes = DEFAULT_NOTES_GENERIC_RELATION()

        @classmethod
        def getSearchableFields(self):
            result = super(AbstractInstrumentDataProduct, self).getSearchableFields()
            result.append('flight__name')
            return result

        @property
        def samples(self):
            samples = [(s.wavelength,s.reflectance) for s in self.nirvssspectrometersample_set.all()]
            return samples

        @classmethod
        def getDataForm(cls, instrument_name):
            return None

        @classmethod
        def getSearchFormFields(cls):
            return ['flight__vehicle',
                    'flight',
                    'name',
                    'description',
                    'collector',
                    'creator',
                    ]

        @classmethod
        def getSearchFieldOrder(cls):
            return ['flight__vehicle',
                    'flight',
                    'name',
                    'description',
                    'collector',
                    'creator',
                    'acquisition_timezone',
                    'min_acquisition_time',
                    'max_acquisition_time']

        def __unicode__(self):
            return "%s @ %s" % (self.instrument.shortName,
                                self.acquisition_time)


class NirvssSpectrometerSample(models.Model):
    dataProduct = models.ForeignKey(NirvssSpectrometerDataProduct)
    wavelength = models.IntegerField(db_index=True)
    reflectance = models.FloatField(db_index=True)

    class Meta:
        ordering = ['dataProduct', 'wavelength']

    def __unicode__(self):
        return "%s: (%d, %f)" % (self.dataProduct.name,
                                 self.wavelength, self.reflectance)


class WallDistance(xgds_timeseries.TimeSeriesModel):
    """
    This is an auto-generated Django model created from a
    YAML specifications using ./apps/xgds_core/importer/yamlModelBuilder.py
    and YAML file ./apps/xgds_braille_app/importer/KRex2_Distance.yaml
    """

    timestamp = models.DateTimeField(db_index=True, null=False, blank=False)
    distance = models.FloatField(null=True, blank=True)
    flight = models.ForeignKey('xgds_core.Flight', on_delete=models.SET_NULL, blank=True, null=True)

    title = 'Wall Distance'

    channel_descriptions = {'distance': xgds_timeseries.ChannelDescription('Wall Distance', 'm', 0, 5, interval=1),
                            }

    @classmethod
    def get_channel_names(cls):
        return ['distance']


class Environmental(xgds_timeseries.TimeSeriesModel):
    """
    This is an auto-generated Django model created from a
    YAML specifications using ./apps/xgds_core/importer/yamlModelBuilder.py
    and YAML file ./apps/xgds_braille_app/importer/KRex2_Environmental.yaml
    """

    timestamp = models.DateTimeField(db_index=True, null=False, blank=False)
    temperature = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    flight = models.ForeignKey('xgds_core.Flight', on_delete=models.SET_NULL, blank=True, null=True)

    title = 'Environmental'

    channel_descriptions = {
                            'temperature': xgds_timeseries.ChannelDescription('Temp', units='C', global_min=0.000000, global_max=45.000000, interval=1),
                            'pressure': xgds_timeseries.ChannelDescription('Pressure', interval=1),
                            'humidity': xgds_timeseries.ChannelDescription('Humidity', global_min=0.000000, global_max=100.000000, interval=1),
                            }

    @classmethod
    def get_channel_names(cls):
        return ['temperature', 'pressure', 'humidity', ]

