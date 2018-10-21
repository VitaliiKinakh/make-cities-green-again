import Processor
import cv2
import numpy as np

# Global section
path_to_cities = "data/cities.shp"
path_to_dataset = "data/cities_database.json"


if __name__ == "__main__":
    proc = Processor.Processor(path_to_cities_geom=path_to_cities, path_to_cities_info=path_to_dataset)
    mask = proc.process_city("LVOV", "rich_green_zone")

    print(mask)