import cv2
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot as plt

#green_lower = (0, 51, 0)
#green_upper = (62, 75, 61)

trees = cv2.imread('trees.png')
buildings = cv2.imread('buildings.png')

trees = cv2.cvtColor(trees, cv2.COLOR_BGR2Lab)
buildings = cv2.cvtColor(buildings, cv2.COLOR_BGR2Lab)

trees_ab = [trees[:, :, 1],trees[:, :, 2]]
buildings_ab = [buildings[:, :, 1],buildings[:, :, 2]]

trees_ab = [trees_ab[0].flatten(), trees_ab[1].flatten()]
buildings_ab = [buildings_ab[0].flatten(), buildings_ab[1].flatten()]

fig = plt.figure()
ax1 = fig.add_subplot(111, projection='3d')


trees_hist, trees_xedges, trees_yedges = np.histogram2d(trees_ab[0], trees_ab[1], bins=64, range=[[0, 256], [0, 256]])
buildings_hist, buildings_xedges, buildings_yedges = np.histogram2d(buildings_ab[0], buildings_ab[1], bins=64, range=[[0, 256], [0, 256]])

buildings_xpos, buildings_ypos = np.meshgrid(buildings_xedges[:-1] + 0.25, buildings_yedges[:-1] + 0.25)
buildings_xpos = buildings_xpos.flatten('F')
buildings_ypos = buildings_ypos.flatten('F')
buildings_zpos = np.zeros_like(buildings_xpos)

# Construct arrays with the dimensions for the 16 bars.
buildings_dx = 0.5 * np.ones_like(buildings_zpos)
buildings_dy = buildings_dx.copy()
buildings_dz = buildings_hist.flatten()

trees_xpos, trees_ypos = np.meshgrid(trees_xedges[:-1] + 0.25, trees_yedges[:-1] + 0.25)
trees_xpos = trees_xpos.flatten('F')
trees_ypos = trees_ypos.flatten('F')
trees_zpos = np.zeros_like(trees_xpos)

# Construct arrays with the dimensions for the 16 bars.
trees_dx = 0.5 * np.ones_like(trees_zpos)
trees_dy = trees_dx.copy()
trees_dz = trees_hist.flatten()

ax1.bar3d(trees_xpos, trees_ypos, trees_zpos, trees_dx, trees_dy, trees_dz, color='b', zsort='average')
ax1.bar3d(buildings_xpos, buildings_ypos, buildings_zpos, buildings_dx, buildings_dy, buildings_dz, color='r', zsort='average')

plt.show()


