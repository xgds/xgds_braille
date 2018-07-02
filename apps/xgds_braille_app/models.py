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

from geocamTrack.models import AbstractTrack, DEFAULT_ICON_STYLE_FIELD, DEFAULT_LINE_STYLE_FIELD, \
    AltitudeResourcePosition, TrackMixin
from xgds_timeseries.models import TimeSeriesModel, ChannelDescription
from xgds_map_server.models import GeoJSON
from xgds_core.models import AbstractActiveFlight, HasVehicle
from xgds_planner2.models import AbstractPlanExecution
from xgds_core.models import AbstractFlight, DEFAULT_VEHICLE_FIELD, AbstractGroupFlight
from xgds_instrument.models import ScienceInstrument, AbstractInstrumentDataProduct
from xgds_notes2.models import NoteLinksMixin, NoteMixin, DEFAULT_NOTES_GENERIC_RELATION
from xgds_core.models import HasFlight


class BrailleTrackMixin(models.Model):
    track = models.ForeignKey('xgds_braille_app.BrailleTrack')

    @property
    def has_track(self):
        return hasattr(self, 'track')

    @property
    def track_name(self):
        if self.has_track:
            return self.track.name
        return None

    @property
    def track_pk(self):
        if self.has_track:
            return self.track.pk
        return None

    @property
    def track_color(self):
        if self.has_track:
            return self.track.getLineStyleColor()
        return None

    @property
    def track_hexcolor(self):
        if self.has_track:
            kc = self.track.getLineStyleColor()
            nc = '%s%s%s' % (kc[6:], kc[4:6], kc[2:4])
            return nc
        return None

    class Meta:
        abstract = True

class BrailleTrack(AbstractTrack, HasVehicle):
    iconStyle = DEFAULT_ICON_STYLE_FIELD()
    lineStyle = DEFAULT_LINE_STYLE_FIELD()
    flight = models.ForeignKey('xgds_braille_app.BrailleFlight', null=True, blank=True)
    vehicle = DEFAULT_VEHICLE_FIELD()

    def __unicode__(self):
        return '%s %s' % (self.__class__.__name__, self.name)

class PastResourcePosition(AltitudeResourcePosition, BrailleTrackMixin):
    @classmethod
    def getSearchFormFields(cls):
        return ['track', 'track__vehicle', 'timestamp', 'latitude', 'longitude', 'altitude']

class BandDepthGeoJSON(GeoJSON):
    flight = models.ForeignKey('xgds_braille_app.BrailleFlight', null=True, blank=True)

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
    flight = models.ForeignKey('xgds_braille_app.BrailleFlight', on_delete=models.SET_NULL, blank=True, null=True)

    channel_descriptions = {
        'band_depth': ChannelDescription('Band Depth', units='C', global_min=-5.0, global_max=5.0)
    }

    @classmethod
    def get_channel_names(cls):
        return ['band_depth']

    def __unicode__ (self):
        return "ts: %s, band depth %s, bd name: %s" % (self.time_stamp, self.band_depth, self.band_depth_definition.name)

class ActiveFlight(AbstractActiveFlight):
    flight = models.ForeignKey('xgds_braille_app.BrailleFlight', null=True, blank=True)

class PlanExecution(AbstractPlanExecution):
    plan = models.ForeignKey('xgds_planner2.Plan', null=True, related_name='xgds_braille_plan_execution')
    flight = models.ForeignKey('xgds_braille_app.BrailleFlight', null=True, blank=True)

class GroupFlight(AbstractGroupFlight):
    @property
    def flights (self):
        return self.brailleflight_set.all()

class BrailleFlight(AbstractFlight):
    group   = models.ForeignKey('xgds_braille_app.GroupFlight', null=True, blank=True)
    vehicle = DEFAULT_VEHICLE_FIELD()
    summary = models.CharField(max_length=1024, blank=True, null=True)
    geojson = models.ForeignKey('xgds_map_server.GeoJSON', null=True, blank=True)

    def has_nirvss_data(self):
        return (self.geojson is not None) and self.geojson.is_nirvss_data()

    def getTreeJsonChildren(self):
        children = []

        if hasattr(self, 'track'):
            children.append({
                 "title"   : "Track",
                 "selected": False,
                 "tooltip" : "Tracks for " + self.name,
                 "key"     : self.uuid + "_tracks",
                 "data"    : {
                     "json"   : reverse('geocamTrack_mapJsonTrack', kwargs={'uuid': str(self.track.uuid)}),
                     "kmlFile": reverse('geocamTrack_trackKml', kwargs={'trackName': self.track.name}),
                     "sseUrl" : "",
                     "type"   : 'MapLink',
                 }
            })

        if self.plans:
            my_plan = self.plans[0].plan
            children.append({
                 "title"   : "Plan",
                 "selected": False,
                 "tooltip" : "Plan for " + self.name,
                 "key"     : self.uuid + "_plan",
                 "data"    : {
                     "json"   : reverse('planner2_mapJsonPlan', kwargs={'uuid': str(my_plan.uuid)}),
                     "kmlFile": reverse('planner2_planExport', kwargs={'uuid': str(my_plan.uuid), 'name': my_plan.name + '.kml'}),
                        "sseUrl" : "",
                        "type"   : 'MapLink',
                 }
            })

        if self.has_nirvss_data():
            # this will be changed in the future

            children.append({
                 "title"   : "NIRVSS heatmap",
                 "selected": False,
                 "tooltip" : "GeoJSON object for " + self.name,
                 "key"     : self.uuid + "_plan",
                 "data"    : {
                    "type"   : "GeoJSON",
                    "geoJSON": self.geojson.geoJSON,
                 }
            })
        return children

class NirvssSpectrometerDataProduct(AbstractInstrumentDataProduct, NoteLinksMixin, NoteMixin, HasFlight):
        flight = models.ForeignKey(settings.XGDS_CORE_FLIGHT_MODEL, null=True, blank=True)
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

class WallDistance(TimeSeriesModel):
    """
    This is an auto-generated Django model created from a
    YAML specifications using ./apps/xgds_core/importer/yamlModelBuilder.py
    and YAML file ./apps/xgds_braille_app/importer/KRex2_Distance.yaml
    """

    timestamp = models.DateTimeField(db_index=True, null=False, blank=False)
    distance = models.FloatField(null=True, blank=True)
    flight = models.ForeignKey('xgds_core.Flight', on_delete=models.SET_NULL, blank=True, null=True)

    title = 'Wall Distance'

    channel_descriptions = {'distance': ChannelDescription('Wall Distance', 'm', 0, 5, interval=1),
                            }

    @classmethod
    def get_channel_names(cls):
        return ['distance']

class Environmental(TimeSeriesModel):
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
                            'temperature': ChannelDescription('Temp', units='C', global_min=0.000000, global_max=45.000000, interval=1),
                            'pressure': ChannelDescription('Pressure', interval=1),
                            'humidity': ChannelDescription('Humidity', global_min=0.000000, global_max=100.000000, interval=1),
                            }

    @classmethod
    def get_channel_names(cls):
        return ['temperature', 'pressure', 'humidity', ]

