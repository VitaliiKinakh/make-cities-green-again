import DatabaseManager
import cv2
import numpy as np

# Global section
path_to_cities = "data/cities.shp"
path_to_dataset = "data/cities_database.json"

north_starttime = "2018-04-01"
north_endtime = "2018-08-01"
south_starttime = "2017-11-01"
south_endtime = "2018-03-01"


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


if __name__ == "__main__":
    proc = DatabaseManager.Processor(path_to_cities_geom=path_to_cities, path_to_cities_info=path_to_dataset)
    lvov = proc.find_city_in_db("LVOV")

    proc.get_raster_for_city(lvov)

    trees_and_some_shrubs_threshold = 0.32
    trees_shrubs_grass = 0

    # mask = proc.mask_image_based_on_color(image)
    #
    # masked = cv2.bitwise_and(image, image, mask=mask)
    #
    # cv2.imwrite("data/images/LVOV_masked.tif", masked)

