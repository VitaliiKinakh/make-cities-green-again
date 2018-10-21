import descarteslabs as dl
import numpy as np
import geopandas as gpd
import os
import json
import cv2 as cv
from collections import defaultdict
import gdal
import tifffile


green_zones = {
    "rich_green_zone": {
        "lower_ndvi_thresh": 0,
        "upper_ndvi_thresh": 1,
        "lower_bound": (0, 81, 0),
        "upper_bound": (255, 180, 60),
        "color_code": cv.COLOR_BGR2HSV
    },
    "medium_green_zone": {
        "lower_ndvi_thresh": 0,
        "upper_ndvi_thresh": 1,
        "lower_bound": (0, 60, 0),
        "upper_bound": (255, 180, 50),
        "color_code": cv.COLOR_BGR2HSV
    },
    "poor_green_zone": {
        "lower_ndvi_thresh": 0,
        "upper_ndvi_thresh": 1,
        "lower_bound": (0, 0, 55),
        "upper_bound": (255, 180, 230),
        "color_code": cv.COLOR_BGR2HSV
    },
    "very_poor_green_zone": {
        "upper_ndvi_thresh": 1,
        "lower_ndvi_thresh": 0,
        "lower_bound": (0, 0, 50),
        "upper_bound": (255, 180, 255),
        "color_code": cv.COLOR_BGR2HSV
    }
}


class Processor:
    def __init__(self, path_to_cities_geom, path_to_cities_info):
        self.path_to_cities_geom = path_to_cities_geom
        self.path_to_cities_info = path_to_cities_info

        self.cities_geometry = gpd.read_file(self.path_to_cities_geom)

        if os.path.exists(os.path.join(self.path_to_cities_info)):
            with open(os.path.join(self.path_to_cities_info), 'r') as infile:
                self.cities_info = json.loads(infile.read())
        else:
            self.cities_info = defaultdict(dict)
        self.raster_client = dl.Raster()
        self.metadata_client = dl.Metadata()

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
        city_name = city["NAME"].values[0]
        if city_name in self.cities_info.keys() and \
                "raster_filename" in self.cities_info[city_name].keys():
            return self.cities_info["raster_filename"]

        bb = self.find_bb_for_city(city)
        centroid = city["geometry"].centroid

        curr_starttime, curr_endtime = self.get_start_end_time(centroid)

        scenes, ctx = dl.scenes.search(bb, products=["landsat:LC08:01:RT:TOAR"],
                                       start_datetime=curr_starttime, end_datetime=curr_endtime, cloud_fraction=0.1,
                                       limit=1)

        if len(scenes) == 0:
            return None

        scene = scenes[0]
        image_id = scene.properties["id"]

        raster_filename = city["NAME"].values[0]

        self.raster_client.raster(inputs=[image_id], bands=['red', 'green', 'blue', 'alpha'],
                                  scales=[[0, 5500], [0, 5500], [0, 5500], None],
                                  data_type='Byte', cutline=bb, save=True,
                                  outfile_basename="data/images/" + raster_filename,
                                  resolution=15)
        self.cities_info[city_name]["raster_filename"] = "data/images/" + raster_filename + ".tif"

        if "image_width" not in self.cities_info[city_name].keys():
            raster_image = cv.imread("data/images/" + raster_filename + ".tif")
            self.cities_info[city_name]["image_width"] = raster_image.shape[1]
            self.cities_info[city_name]["image_height"] = raster_image.shape[0]

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
    def mask_image_based_on_color(image, green_zone):
        converted_image = cv.cvtColor(image, green_zone["color_code"])
        mask = cv.inRange(converted_image, green_zone["lower_bound"], green_zone["upper_bound"])
        return mask

    def get_ndvi_for_city(self, city):
        if city["NAME"].values[0] in self.cities_info.keys() and \
                "ndvi_raster_filename" in self.cities_info[city["NAME"].values[0]].keys():
            return self.cities_info["ndvi_raster_filename"]

        bb = self.find_bb_for_city(city)
        centroid = city["geometry"].centroid

        curr_starttime, curr_endtime = self.get_start_end_time(centroid)

        fc = self.metadata_client.search(products="modis:09:CREFL", geom=bb, start_time=curr_starttime,
                                         end_time=curr_endtime, limit=1)

        band_info = self.metadata_client.get_band("modis:09:CREFL:ndvi")
        physical_range = band_info['physical_range']
        data_range = band_info['data_range']

        feat_ids = [feat['id'] for feat in fc['features']]

        arr, meta = self.raster_client.ndarray(
            feat_ids,
            cutline=bb,
            bands=['ndvi', 'alpha'],
            scales=[[data_range[0], data_range[1], physical_range[0], physical_range[1]], None],
            data_type='Float32',
            resolution=15)

        nodata = arr[:, :, -1] == 0
        masked = np.where(nodata, 0, arr[:, :, 0])

        tifffile.imsave("data/images/" + city["NAME"].values[0] + "_NDVI" + ".tif", masked)
        self.cities_info[city["NAME"].values[0]]["ndvi_raster_filename"] = "data/images/" + city["NAME"].values[0] + \
                                                                           "_NDVI" + ".tif"
        self.save_database()
        return self.cities_info[city["NAME"].values[0]]["ndvi_raster_filename"]

    def get_ndvi_raster_for_city(self, city):
        if city["NAME"].values[0] in self.cities_info.keys() and \
                "ndvi_raster_filename" in self.cities_info[city["NAME"].values[0]].keys():
            return self.cities_info["ndvi_raster_filename"]

        bb = self.find_bb_for_city(city)
        centroid = city["geometry"].centroid

        curr_starttime, curr_endtime = self.get_start_end_time(centroid)

        fc = self.metadata_client.search(products="modis:09:CREFL", geom=bb, start_datetime=curr_starttime,
                                         end_datetime=curr_endtime, limit=1)
        band_info = self.metadata_client.get_band("modis:09:CREFL:ndvi")
        physical_range = band_info['physical_range']
        data_range = band_info['data_range']

        feat_ids = [feat['id'] for feat in fc['features']]

        self.raster_client.raster(inputs=feat_ids, bands=['ndvi', 'alpha'],
                                  scales=[[data_range[0], data_range[1], physical_range[0], physical_range[1]], None],
                                  data_type='Float32', cutline=bb,
                                  save=True,
                                  outfile_basename="data/images/" + city["NAME"].values[0] + "_NDVI",
                                  resolution=15)
        self.cities_info[city["NAME"].values[0]]["ndvi_raster_filename"] = "data/images/" + city["NAME"].values[0] + "_NDVI" + ".tif"
        return self.cities_info[city["NAME"].values[0]]["ndvi_raster_filename"]

    @staticmethod
    def mask_image_based_on_ndvi(image, green_zone):
        normalized = cv.normalize(image, None, alpha=0, beta=1, norm_type=cv.NORM_MINMAX, dtype=cv.CV_32F)
        mask = cv.inRange(normalized, green_zone["lower_ndvi_thresh"], green_zone["upper_ndvi_thresh"])
        return mask

    def get_city_info(self, city_name):
        city_name = city_name.upper()
        city = self.find_city_in_db(city_name)
        if city_name not in self.cities_info.keys() or "raster_filename" not in self.cities_info[city_name].keys():
            _ = self.get_raster_for_city(city)
            self.save_database()
        bb_df = city.bounds
        minx = bb_df["miny"].values[0]
        miny = bb_df["minx"].values[0]
        maxx = bb_df["maxy"].values[0]
        maxy = bb_df["maxx"].values[0]

        return [minx, miny, maxx, maxy, self.cities_info[city_name]["image_width"],
                self.cities_info[city_name]["image_height"]]

    def process_city(self, city_name, green_zone_name):
        if green_zone_name in self.cities_info[city_name].keys():
            mask = cv.imread(self.cities_info[city_name][green_zone_name])
            return mask

        green_zone = green_zones[green_zone_name]

        city = self.find_city_in_db(city_name)

        if len(city) == 0:
            return None

        if city_name not in self.cities_info.keys() or "raster_filename" not in self.cities_info[city_name]:
            raster_filename = self.get_raster_for_city(city)
        else:
            raster_filename = self.cities_info[city_name]["raster_filename"]

        raster_image = cv.imread(raster_filename)
        mask_based_on_color = self.mask_image_based_on_color(raster_image, green_zone)

        if "ndvi_raster_filename" not in self.cities_info[city_name]:
            ndvi_raster_filename = self.get_ndvi_for_city(city)
        else:
            ndvi_raster_filename = self.cities_info[city_name]["ndvi_raster_filename"]

        ds = gdal.Open(ndvi_raster_filename)
        print(ndvi_raster_filename)
        ndvi_raster_image = np.array(ds.GetRasterBand(1).ReadAsArray())

        print(np.max(ndvi_raster_image))

        mask_based_on_ndvi = self.mask_image_based_on_ndvi(ndvi_raster_image, green_zone)

        combined_mask = cv.bitwise_and(mask_based_on_color, mask_based_on_ndvi)

        black_values = combined_mask == 0
        blank_image = np.zeros(combined_mask.shape, np.uint8)

        green_chanel = np.where(black_values, 0, 255)
        mask = cv.merge((blank_image, green_chanel.astype(np.uint8), blank_image))

        cv.imwrite("data/images/" + city_name + green_zone_name + ".png", mask)
        self.cities_info[city_name][green_zone_name] = "data/images/" + city_name + green_zone_name + ".png"
        self.save_database()

        return mask

    def save_database(self):
        with open(self.path_to_cities_info, 'w') as outfile:
            outfile.write(json.dumps(self.cities_info))
