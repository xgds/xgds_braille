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
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from geocamUtil.loader import LazyGetModelByName

from xgds_timeseries.models import TimeSeriesModel, ChannelDescription
from xgds_map_server.models import GeoJSON
from xgds_instrument.models import ScienceInstrument, AbstractInstrumentDataProduct
from xgds_notes2.models import NoteLinksMixin, NoteMixin, DEFAULT_NOTES_GENERIC_RELATION
from xgds_core.models import HasFlight, DEFAULT_FLIGHT_FIELD, IsFlightChild, IsFlightData


class BandDepthGeoJSON(GeoJSON, IsFlightChild):
    flight = models.ForeignKey(settings.XGDS_CORE_FLIGHT_MODEL, null=True, blank=True)
    band_depth_definition = models.ForeignKey('xgds_braille_app.BandDepthDefinition', null=True, blank=True)

    @classmethod
    def get_tree_json(cls, parent_class, parent_pk):
        try:
            found = cls.objects.filter(flight__id=parent_pk)
            result = []
            for f in found:
                result.append({
                    "title": "NIRVSS heatmap for %s" % f.band_depth_definition.name,
                    "selected": False,
                    "tooltip": "NIRVSS heatmap for %s taken on flight %s" % (
                    f.band_depth_definition.name, f.flight.name),
                    "key": f.pk + "_nirvss",
                    "data": {
                        "type": "GeoJSON",
                        "geoJSON": f.geoJSON,
                    }
                })
            return result
        except ObjectDoesNotExist:
            return None

    def __unicode__(self):
        return "band depth geojson for flight %s and bdd %s" % (self.flight.name, self.band_depth_definition.name)


class BandDepthDefinition(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    left_wavelength = models.FloatField()
    center_wavelength = models.FloatField()
    right_wavelength = models.FloatField()

    def __unicode__ (self):
        return "%s between %s nm and %s nm, center %s nm" % (self.name, self.left_wavelength, self.right_wavelength, self.center_wavelength)


class BandDepthTimeSeries(TimeSeriesModel):
    time_stamp = models.DateTimeField(db_index=True, null=False, blank=False)
    band_depth = models.FloatField(null=True, blank=True)
    band_depth_definition = models.ForeignKey('xgds_braille_app.BandDepthDefinition', blank=True, null=True)
    flight = models.ForeignKey(settings.XGDS_CORE_FLIGHT_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    title = "Band Depth Time Series"

    dynamic = True
    dynamic_value = "band_depth"
    dynamic_separator = "band_depth_definition_name"

    @staticmethod
    def get_all_band_depth_defs():
        return list(BandDepthDefinition.objects.all())

    @property
    def channel_description(self):
        descriptions = {}
        for bdd in self.get_all_band_depth_defs():
            descriptions[bdd.name] = ChannelDescription(bdd.name, global_min=-15.0, global_max=15.0)
        return descriptions

    @classmethod
    def get_channel_names(cls):
        return [bdd.name for bdd in cls.get_all_band_depth_defs()]

    @property
    def band_depth_definition_name(self):
        return self.band_depth_definition.name

    def __unicode__ (self):
        return "ts: %s, band depth %s, bd name: %s" % (self.time_stamp, self.band_depth, self.band_depth_definition.name)


class NirvssSpectrometerDataProduct(AbstractInstrumentDataProduct, NoteLinksMixin, NoteMixin, HasFlight, IsFlightData):
    flight = models.ForeignKey(settings.XGDS_CORE_FLIGHT_MODEL, null=True, blank=True)
    notes = DEFAULT_NOTES_GENERIC_RELATION()

    @classmethod
    def get_info_json(cls, flight_pk):
        found = NirvssSpectrometerDataProduct.objects.filter(flight__id=flight_pk)
        result = None
        if found.exists():
            flight = LazyGetModelByName(settings.XGDS_CORE_FLIGHT_MODEL).get().objects.get(id=flight_pk)
            result = {'name': 'NIRVSS Spectra',
                      'count': found.count(),
                      'url': reverse('search_map_object_filter',
                                     kwargs={'modelName': 'Spectrometer',
                                             'filter': 'flight__group:%d,flight__vehicle:%d' % (
                                             flight.group.pk, flight.vehicle.pk)})
                      }
        return result

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


class WallDistance(TimeSeriesModel):
    """
    This is an auto-generated Django model created from a
    YAML specifications using ./apps/xgds_core/importer/yamlModelBuilder.py
    and YAML file ./apps/xgds_braille_app/importer/KRex2_Distance.yaml
    """

    timestamp = models.DateTimeField(db_index=True, null=False, blank=False)
    distance = models.FloatField(null=True, blank=True)
    flight = models.ForeignKey(settings.XGDS_CORE_FLIGHT_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    title = 'Wall Distance'

    channel_descriptions = {'distance': ChannelDescription('Wall Distance', 'm', 0, 5, interval=1),
                            }

    @classmethod
    def get_channel_names(cls):
        return ['distance']


class InstrumentPlatformTilt(TimeSeriesModel):
    """
    This is an auto-generated Django model created from a
    YAML specifications using ./submodules/xgds_core/xgds_core/importer/yamlModelBuilder.py
    and YAML file apps/xgds_braille_app/importer/KRex2_Tilt.yaml
    """

    timestamp = models.DateTimeField(db_index=True, null=False, blank=False)
    tilt = models.FloatField(null=True, blank=True)
    flight = models.ForeignKey(settings.XGDS_CORE_FLIGHT_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    title = 'Instrument Platform Tilt'
    channel_descriptions = {
                            'tilt': ChannelDescription('Tilt', units='degrees'),
                            }

    @classmethod
    def get_channel_names(cls):
        return ['tilt', ]


class InstrumentPlatformLight(TimeSeriesModel):
    """
    This is an auto-generated Django model created from a
    YAML specifications using ./apps/xgds_core/importer/yamlModelBuilder.py
    and YAML file ./apps/xgds_braille_app/importer/KRex2_Light.yaml
    """

    timestamp = models.DateTimeField(db_index=True, null=False, blank=False)
    light0 = models.IntegerField(null=True, blank=True)
    light1 = models.IntegerField(null=True, blank=True)
    light2 = models.IntegerField(null=True, blank=True)
    light3 = models.IntegerField(null=True, blank=True)
    flight = models.ForeignKey('xgds_core.Flight', on_delete=models.SET_NULL, blank=True, null=True)

    title = 'Instrument Platform Light'
    channel_descriptions = {
                            'light0': ChannelDescription('Light0'),
                            'light1': ChannelDescription('Light1'),
                            'light2': ChannelDescription('Light2'),
                            'light3': ChannelDescription('Light3'),
                            }

    @classmethod
    def get_channel_names(cls):
        return ['light0', 'light1', 'light2', 'light3', ]

