import descarteslabs as dl
import numpy as np
import geopandas as gpd
import pandas as pd


# Global section
path_to_cities = "data/cities.shp"
# load cities
cities = gpd.read_file(path_to_cities)

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


def get_raster_for_city(city):
    bb = find_bb_for_city(city)

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

    for i, scene in enumerate(scenes):
        images_id = [scene.properties["id"]]
        raster_client = dl.Raster()
        raster_client.raster(inputs=images_id, bands=['red', 'green', 'blue', 'alpha'],
                             scales=[[0, 5500], [0, 5500], [0, 5500], None],
                             data_type='Byte', cutline=bb, save=True, outfile_basename='save_local' + str(i),
                             resolution=15)


if __name__ == "__main__":
    lviv_city = find_city_in_db("LVOV")
    get_raster_for_city(lviv_city)

# # List of id save
# ids = []
#
#
# start_period = "2018-04-01"
# end_period = "2018-08-01"
#
# box =  {
#     "type": "Polygon",
#     "coordinates": [
#         [
#             [
#                 -1,
#                 -8
#             ],
#             [
#                 1,
#                 -8
#             ],
#             [
#                 1,
#                 8
#             ],
#             [
#                 -1,
#                 8
#             ],
#             [
#                 -1,
#                 -8
#             ]
#         ]
#     ]
# }
#
# full_scenes, ctx = dl.scenes.search(box, products=["landsat:LC08:01:RT:TOAR"],
#                                     start_datetime=start_period, end_datetime=end_period, cloud_fraction=0.1,
#                                     limit=15)
#
# scene = full_scenes[0]
#
# print(scene)
#
# tile = dl.scenes.DLTile.from_latlon(45.7230, 15.3966,
#                                     resolution=20.0,
#                                     tilesize=1024,
#                                     pad=0)
#
# # Use the Scenes API to search for imagery availble over the area of interest
# scenes, ctx = dl.scenes.search(tile,
#                                products=["landsat:LC08:01:RT:TOAR"],
#                                start_datetime=start_period,
#                                end_datetime=end_period,
#                                limit=2,
#                                cloud_fraction=.1)
#
# # Pick just one scene
# scene = scenes[0]
#
# for s in scenes:
#     print(s.properties["id"])
#     print(s.properties["tile_id"])
#     print()
#
# # Load the data as an ndarray
# arr = scene.ndarray("red green blue", ctx)
#
# # Display the scene
# dl.scenes.display(arr, size=16, title=scene.properties.id)