import Processor
import cv2
import numpy as np

# Global section
path_to_cities = "data/cities.shp"
path_to_dataset = "data/cities_database.json"

north_starttime = "2018-04-01"
north_endtime = "2018-08-01"
south_starttime = "2017-11-01"
south_endtime = "2018-03-01"


if __name__ == "__main__":
    proc = Processor.Processor(path_to_cities_geom=path_to_cities, path_to_cities_info=path_to_dataset)
    city = proc.find_city_in_db("LVOV")
    mask = proc.process_city("LVOV", "medium_green_zone")

    cv2.namedWindow("Mask", cv2.WINDOW_FREERATIO)
    cv2.imshow("Mask", mask)
    cv2.waitKey(0)