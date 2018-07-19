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

import django
from geocamUtil.loader import LazyGetModelByName
django.setup()
from django.conf import settings
from pandas import DataFrame, merge, to_datetime
from xgds_core.models import Flight
from xgds_braille_app.models import NirvssSpectrometerDataProduct, BandDepthTimeSeries, BandDepthDefinition


def calculate_band_depth(data_frame, wavelengths, sampling_rate="1S"):
    reflectances = [
        data_frame
            .loc[data_frame['wavelength'] == r]
            .drop(['wavelength'], axis=1)
            .set_index('time')
            .rename(index=str, columns={'reflectance': str(r) + 'nm'})
        for r in wavelengths
    ]

    reflectances = merge(
        merge(reflectances[0], reflectances[1], left_index=True, right_index=True),
        reflectances[2], left_index=True, right_index=True,
    )

    reflectances.index = to_datetime(reflectances.index, infer_datetime_format=True, utc=True)

    left, right = reflectances[str(wavelengths[0]) + 'nm'], reflectances[str(wavelengths[2]) + 'nm']

    reflectances['predicted'] = ((right - left) / (wavelengths[2] - wavelengths[0])) * (wavelengths[1] - wavelengths[0]) + left
    reflectances['band_depth'] = 1.0 - (reflectances[str(wavelengths[1]) + 'nm'] / reflectances['predicted'])

    return reflectances[['band_depth']].resample(sampling_rate).mean().dropna()


def convert_nirvss_spectra(flight, instrument):
    data_products = NirvssSpectrometerDataProduct.objects.filter(flight=flight, instrument=instrument)

    samples = []

    for p in data_products:
        samples += [
            {
                "wavelength": s.wavelength,
                "reflectance": s.reflectance,
                "time": p.acquisition_time,
            }
            for s in p.nirvssspectrometersample_set.all()
        ]

    return DataFrame(data=samples)


def add_band_depth_time_series(data_frame, band_depth_definition, flight):
    bdts_objects = []
    for time, band_depth in data_frame.itertuples(name=None):
        bdts_objects.append(BandDepthTimeSeries.objects.create(time_stamp=time, band_depth=band_depth, band_depth_definition=band_depth_definition, flight=flight))
    return bdts_objects


def get_band_depth_definitions():
    return BandDepthDefinition.objects.all()

# main function to be called from outside this script
def create_band_depth_time_series(flight, instrument):
    data_frame = convert_nirvss_spectra(flight, instrument)
    bdts_objects = []
    for bdd in get_band_depth_definitions():
        reflectances = calculate_band_depth(data_frame, [
            bdd.left_wavelength, bdd.center_wavelength, bdd.right_wavelength,
        ])
        bdts_objects += add_band_depth_time_series(reflectances, bdd, flight)
    return bdts_objects




