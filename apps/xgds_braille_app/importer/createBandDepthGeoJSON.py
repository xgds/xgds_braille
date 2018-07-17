#!/usr/bin/env python

'''
This script requires some additional dependencies, which are installed using:
pip install pandas utm colour
'''

import django

from geocamUtil.loader import LazyGetModelByName

django.setup()
from django.conf import settings

from xgds_braille_app.models import BandDepthDefinition, BandDepthGeoJSON, BandDepthTimeSeries

import pandas as pd
from colour import Color
from utm import from_latlon, to_latlon
from json import dumps

colors = list(Color("blue").range_to(Color("red"), 100))

def lat_lon_to_utm(row):
    assert -85  <= row['latitude']  <= 85,  "Got a latitude of %s which is out of bounds"  % row['latitude']
    assert -180 <= row['longitude'] <= 180, "Got a longitude of %s which is out of bounds" % row['longitude']
    return from_latlon(row['latitude'], row['longitude'])

def clip_to_range(minimum, maximum, x):
    return max(minimum, min(x, maximum))

def scale_between(minimum, maximum, x):
    rng = maximum - minimum
    return minimum + x * rng

def get_color(percentage):
    clipped = clip_to_range(0, 0.5, percentage)
    clipped *= 2 # it is now between 0 and 1
    return colors[int(clipped * (len(colors) - 1))]

def create_feature_collection(collection):
    return {
        "type": "FeatureCollection",
        "features": collection,
    }

def create_geojson(easting, northing, zone_number, zone_letter, band_depth, confidence, stddev):
    clipped_confidence = clip_to_range(0, 150, confidence) / 150.0
    radius = scale_between(0.25, 0.5, clipped_confidence)

    # temporary fix
    radius = 0.5

    lat_minus_radius, lng_minus_radius = to_latlon(easting - radius, northing - radius, zone_number, zone_letter)
    lat_plus_radius,  lng_plus_radius  = to_latlon(easting + radius, northing + radius, zone_number, zone_letter)

    return {
        "type": "Feature",
        "properties": 
        {
            "stroke-width": 0,
            "fill": str(get_color(band_depth)),
            "fill-opacity": 1,
            "popup-content":
            {
                "Band Depth": "%f +- %f" % (round(float(band_depth), 4), round(float(stddev), 4)),
                "Confidence": int(confidence),
            }
        },
        "geometry":
        {
            "type": "Polygon",
            "coordinates": 
            [[
                [lng_plus_radius,  lat_minus_radius],
                [lng_minus_radius, lat_minus_radius],
                [lng_minus_radius, lat_plus_radius],
                [lng_plus_radius,  lat_plus_radius],
                [lng_plus_radius,  lat_minus_radius],
            ]]
        }
    }

def create_geojson_for_flight(flight, band_depth_definition):
    band_depth_time_series = BandDepthTimeSeries.objects.filter(
        time_stamp__gte=flight.start_time,
        time_stamp__lte=flight.end_time,
        band_depth_definition=band_depth_definition,
        flight=flight,
    )
    band_depth = []
    for bdts in band_depth_time_series:
        band_depth.append({
            "timestamp": bdts.time_stamp,
            "value": bdts.band_depth,
        })
    band_depth = pd.DataFrame(data=band_depth)
    if len(band_depth) == 0:
        return None

    flight_track_positions = flight.track.getPositions()
    gps = []
    for ftp in flight_track_positions:
        gps.append({
            "timestamp": ftp.timestamp,
            "latitude": float(ftp.latitude),
            "longitude": float(ftp.longitude),
        })
    gps = pd.DataFrame(data=gps)
    if len(gps) == 0:
        return None

    band_depth.index = pd.to_datetime(
        band_depth['timestamp'],
        infer_datetime_format=True,
        utc=True,
    )
    band_depth.sort_index(inplace=True)

    gps.index = pd.to_datetime(
        gps['timestamp'],
        infer_datetime_format=True,
        utc=True,
    )
    gps.sort_index(inplace=True)

    merged_df = pd.merge_asof(
        band_depth,
        gps,
        left_index=True,
        right_index=True,
        direction="nearest",
        suffixes=["_band_depth", "_gps"],
        tolerance=pd.Timedelta('10 seconds'),
    )[[
        "latitude",
        "longitude",
        "value",
    ]].dropna()

    if len(merged_df) == 0:
        return None

    post_df = merged_df.apply(lat_lon_to_utm, axis=1)

    zone_number, zone_letter = post_df.iloc[0][2], post_df.iloc[0][3]

    eastings = post_df.apply(lambda x: x[0]).values
    northings = post_df.apply(lambda x: x[1]).values

    merged_df['easting'] = [int(round(x)) for x in eastings]
    merged_df['northing'] = [int(round(x)) for x in northings]

    merged_df = merged_df[['easting', 'northing', 'value']]

    groups = merged_df.groupby(['easting', 'northing'])

    grouped_df = (
         groups
        .mean().rename(index=str, columns={"value": "mean"})
        .join(groups.count().rename(index=str, columns={"value": "count"}), how="left")
        .join(groups.std().rename(index=str, columns={"value": "std"}), how="left")
    )

    grouped_df.reset_index(inplace=True)

    geojson_collection = []

    for element_index in range(len(grouped_df)):
        element = grouped_df.iloc[element_index]

        geojson_collection.append(create_geojson(
            easting=int(element.at['easting']),
            northing=int(element.at['northing']),
            zone_number=zone_number,
            zone_letter=zone_letter,
            band_depth=element.at['mean'],
            confidence=element.at['count'],
            stddev=element.at['std'],
        ))

    return dumps(create_feature_collection(geojson_collection))

def create_geojson_for_all_bdd(flight):
    for bdd in BandDepthDefinition.objects.all():
        geojson_string = create_geojson_for_flight(
            flight=flight,
            band_depth_definition=bdd,
        )
        if geojson_string is None:
            continue
        BandDepthGeoJSON.objects.create(
            flight=flight,
            band_depth_definition=bdd,
            geoJSON=geojson_string,
        )
