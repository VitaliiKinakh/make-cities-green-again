import descarteslabs as dl
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv


metadata_client = dl.Metadata()
raster_client = dl.Raster()

# A bounding box geometry
aoi = {
    "type": "Polygon",
    "coordinates": [
        [
            [
                -105.86975097656249,
                36.94550173495345
            ],
            [
                -104.930419921875,
                36.94550173495345
            ],
            [
                -104.930419921875,
                37.70120736474139
            ],
            [
                -105.86975097656249,
                37.70120736474139
            ],
            [
                -105.86975097656249,
                36.94550173495345
            ]
        ]
    ]
}


# Request Modis imagery, which contains indicies that need to be scaled
fc = metadata_client.search(products="modis:09:CREFL", geom=aoi, start_time="2017-05-01",
                            end_time="2018-05-15", limit=1)

# Fetch the band information using the Metadata API, including the NDVI ranges
band_info = metadata_client.get_band("modis:09:CREFL:ndvi")
physical_range = band_info['physical_range']
data_range = band_info['data_range']

# Isolate the image IDs to pull data for
feat_ids = [feat['id'] for feat in fc['features']]


# Request the NDVI band and scale it accordingly and the alpha band for masking next
arr, meta = raster_client.ndarray(
    feat_ids,
    cutline=aoi,
    bands=['ndvi', 'alpha'],
    scales=[[data_range[0], data_range[1], physical_range[0], physical_range[1]], None],
    data_type='Float32',
    resolution=15)

# mask out nodata pixels
nodata = arr[:, :, -1] == 0
masked = np.where(nodata, 0, arr[:, :, 0])

print(arr.shape)
print(np.max(arr[:, :, 0]))
print(np.mean(arr[:, :, 0]))

cv.namedWindow("NDVI", cv.WINDOW_FREERATIO)
cv.imshow("NDVI", masked)
cv.waitKey(0)

# plt.hist(masked)
