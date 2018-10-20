import descarteslabs as dl
import numpy as np
import geopandas as gpd
import pandas as pd
import os
import json


# Global section
path_to_cities = "data/cities.shp"
path_to_dataset = "data/cities_database.json"

north_starttime = "2018-04-01"
north_endtime = "2018-08-01"
south_starttime = "2017-11-01"
south_endtime = "2018-03-01"


def find_city_in_db(name):
    name = name.upper()
    curr_city = cities[cities["NAME"] == name]
    return curr_city


def find_bb_for_city(city_data):
    bb_df = city_data.bounds

    minx = bb_df["minx"].values[0]
    miny = bb_df["miny"].values[0]
    maxx = bb_df["maxx"].values[0]
    maxy = bb_df["maxy"].values[0]

    bb_gjson = {
        "type": "Polygon",
        "coordinates": [[[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny]]]
    }
    return bb_gjson


def get_raster_for_city(city, filename):
    bb = find_bb_for_city(city)

    print(bb)

    centroid = city["geometry"].centroid
    lat = centroid.values[0].y

    if lat >= 0:
        curr_starttime = north_starttime
        curr_endtime = north_endtime
    else:
        curr_starttime = south_endtime
        curr_endtime = south_starttime

    scenes, ctx = dl.scenes.search(bb, products=["landsat:LC08:01:RT:TOAR"],
                                        start_datetime=curr_starttime, end_datetime=curr_endtime, cloud_fraction=0.1,
                                        limit=15)

    scene = scenes[0]
    print(scene.properties)
    images_id = [scene.properties["id"]]
    raster_client = dl.Raster()
    raster_client.raster(inputs=images_id, bands=['red', 'green', 'blue', 'alpha'],
                         scales=[[0, 5500], [0, 5500], [0, 5500], None],
                         data_type='Byte', cutline=bb, save=True, outfile_basename='filename' + image_id,
                         resolution=15)


if __name__ == "__main__":
    # load cities geometry
    cities = gpd.read_file(path_to_cities)

    # load database where information is stored
    if os.path.exists(os.path.join(path_to_dataset)):
        with open(os.path.join(path_to_dataset), 'r') as infile:
            cities_dataset = json.loads(infile.read())
    else:
        cities_dataset = dict()

    lviv_city = find_city_in_db("LVOV")
    get_raster_for_city(lviv_city, "LVOV")