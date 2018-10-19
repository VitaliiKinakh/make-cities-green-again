import descarteslabs as dl
import numpy as np

# List of id save
ids = []


start_period = "2018-04-01"
end_period = "2018-08-01"

box =  {
    "type": "Polygon",
    "coordinates": [
        [
            [
                -179,
                -89
            ],
            [
                179,
                -89
            ],
            [
                179,
                89
            ],
            [
                -179,
                89
            ],
            [
                -179,
                -89
            ]
        ]
    ]
}

full_scenes, ctx = dl.scenes.search(box, products=["landsat:LC08:01:RT:TOAR"],
                                    start_datetime=start_period, end_datetime=end_period, cloud_fraction=0.1,
                                    limit=15)

scene = full_scenes[0]

print(scene)

tile = dl.scenes.DLTile.from_latlon(45.7230, 15.3966,
                                    resolution=20.0,
                                    tilesize=1024,
                                    pad=0)

# Use the Scenes API to search for imagery availble over the area of interest
scenes, ctx = dl.scenes.search(tile,
                               products=["landsat:LC08:01:RT:TOAR"],
                               start_datetime=start_period,
                               end_datetime=end_period,
                               limit=2,
                               cloud_fraction=.1)

# Pick just one scene
scene = scenes[0]

for s in scenes:
    print(s.properties["id"])
    print(s.properties["tile_id"])
    print()

# Load the data as an ndarray
arr = scene.ndarray("red green blue", ctx)

# Display the scene
dl.scenes.display(arr, size=16, title=scene.properties.id)