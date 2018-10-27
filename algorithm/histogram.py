import cv2
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot as plt
import sys
from loadImage import *


#green_lower = (0, 51, 0)
#green_upper = (62, 75, 61)

def plot_histogram_HS (image, parts, fig, color):

    image = [image[:, :, parts[0]],image[:, :, parts[1]]]

    image = [image[0].flatten(), image[1].flatten()]

    image_hist, image_xedges, image_yedges = np.histogram2d(image[0], image[1], bins=64, range=[[0, 256], [0, 256]])

    image_xpos, image_ypos = np.meshgrid(image_xedges[:-1] + 0.25, image_yedges[:-1] + 0.25)
    image_xpos = image_xpos.flatten('F')
    image_ypos = image_ypos.flatten('F')
    image_zpos = np.zeros_like(image_xpos)

    # Construct arrays with the dimensions for the 16 bars.
    image_dx = 0.5 * np.ones_like(image_zpos)
    image_dy = image_dx.copy()
    image_dz = image_hist.flatten()

    ax1.bar3d(image_xpos, image_ypos, image_zpos, image_dx, image_dy, image_dz, color=color, zsort='average')


if __name__ == "__main__":
    trees = [load_image('test_dataset/trees{}.png'.format(i)) for i in range(1,26)]
    non-trees = [load_image('test_dataset/non-trees{}.png'.format(i)) for i in range(1,26)]
    #
    # trees = load_image('test_dataset/trees.png')
    # if trees is None:
    #     sys.exit('Fail while loading image')
    #
    # buildings = load_image('test_dataset/buildings.png')
    # if trees is None:
    #     sys.exit('Fail while loading image')
    #
    # fig = plt.figure()
    # ax1 = fig.add_subplot(111, projection='3d')
    #
    # trees = cv2.cvtColor(trees, cv2.COLOR_BGR2HSV)
    # buildings = cv2.cvtColor(buildings, cv2.COLOR_BGR2HSV)
    #
    # plot_histogram_HS(trees, [0,1], ax1, 'r')
    # plot_histogram_HS(buildings, [0,1], ax1, 'b')
    # plt.show()




