import descarteslabs as dl
import numpy as np
import geopandas as gpd
import pandas as pd
import os
import json
import cv2 as cv


class Processor:
    def __init__(self, path_to_cities_geom, path_to_cities_info):
        self.path_to_cities_geom = path_to_cities_geom
        self.path_to_cities_info = path_to_cities_info

        self.cities_geometry = gpd.read_file(self.path_to_cities_geom)

        if os.path.exists(os.path.join(self.path_to_cities_info)):
            with open(os.path.join(self.path_to_cities_info), 'r') as infile:
                self.cities_info = json.loads(infile.read())
        else:
            self.cities_info = dict()

    @staticmethod
    def get_start_end_time(centroid):
        lat = centroid.values[0].y

        if lat >= 0:
            curr_starttime = "2018-04-01"
            curr_endtime = "2018-08-01"
        else:
            curr_starttime = "2017-11-01"
            curr_endtime = "2018-03-01"
        return curr_starttime, curr_endtime

    def find_city_in_db(self, city_name):
        name = city_name.upper()
        curr_city = self.cities_geometry[self.cities_geometry["NAME"] == name]
        return curr_city

    @staticmethod
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

    def get_raster_for_city(self, city):
        bb = self.find_bb_for_city(city)
        centroid = city["geometry"].centroid

        curr_starttime, curr_endtime = self.get_start_end_time(centroid)

        scenes, ctx = dl.scenes.search(bb, products=["landsat:LC08:01:RT:TOAR"],
                                       start_datetime=curr_starttime, end_datetime=curr_endtime, cloud_fraction=0.1,
                                       limit=15)

        if len(scenes) == 0:
            return None

        scene = scenes[0]
        image_id = scene.properties["id"]
        raster_client = dl.Raster()
        raster_filename = city["NAME"].values[0]

        if city["NAME"].values[0] in self.cities_info.keys():
            return "data/images/" + city["NAME"].values[0] + ".tif"

        raster_client.raster(inputs=[image_id], bands=['red', 'green', 'blue', 'alpha'],
                             scales=[[0, 5500], [0, 5500], [0, 5500], None],
                             data_type='Byte', cutline=bb, save=True, outfile_basename="data/images/" + raster_filename,
                             resolution=15)
        self.cities_info[city["NAME"].values[0]] = {"raster_filename": "data/images/" + raster_filename + ".tif",
                                          "trees_mask_raster_filename": None,
                                          "green_percentage": None,
                                          "money_earned": None}
        return "data/images/" + raster_filename + ".tif"

    @staticmethod
    def refine_image(image):
        clahe = cv.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))

        lab_image = cv.cvtColor(image, cv.COLOR_BGR2Lab)
        l, a, b = cv.split(lab_image)
        c1 = clahe.apply(l)

        merged = cv.merge((c1, a, b))

        merged_rgb = cv.cvtColor(merged, cv.COLOR_Lab2BGR)

        cv.namedWindow("Image", cv.WINDOW_FREERATIO)
        cv.imshow("Image", merged_rgb)
        cv.waitKey(0)

    @staticmethod
    def adjust_gamma(image, gamma=1.0):
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255
                          for i in np.arange(0, 256)]).astype("uint8")
        return cv.LUT(image, table)

    @staticmethod
    def mask_image_based_on_color(image):
        image_lab = cv.cvtColor(image, cv.COLOR_BGR2Lab)
        mask = cv.inRange(image_lab, (0, 105, 101), (255, 131, 121))
        return mask

    def get_ndvi_raster_for_city(self, city):


