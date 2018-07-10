#!/usr/bin/env python

import django
from geocamUtil.loader import LazyGetModelByName
django.setup()
from django.conf import settings
from pandas import DataFrame, merge, to_datetime
from xgds_core.models import Flight
from xgds_braille_app.models import NirvssSpectrometerDataProduct, BandDepthTimeSeries, BandDepthDefinition


def calculate_band_depth(data_frame, wavelengths, sampling_rate="1T"):
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


def convert_nirvss_spectra(start_time, end_time):
    data_products = NirvssSpectrometerDataProduct.objects.filter(instrument_id=1).filter(acquisition_time__gte=start_time, acquisition_time__lte=end_time)
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


def get_flight(flight_name):
    return Flight.objects.get(name=flight_name)


def get_band_depth_definitions():
    return BandDepthDefinition.objects.all()

# main function to be called from outside this script
def create_band_depth_time_series(flight):
    start, end = flight.start_time, flight.end_time
    data_frame = convert_nirvss_spectra(start, end)

    for bdd in get_band_depth_definitions():
        reflectances = calculate_band_depth(data_frame, [
            bdd.left_wavelength, bdd.center_wavelength, bdd.right_wavelength,
        ])

        add_band_depth_time_series(reflectances, bdd, flight)




