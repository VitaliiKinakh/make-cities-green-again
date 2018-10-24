import cv2
import numpy as np

def nothing(x):
    pass

image = cv2.imread('LVOV.tif')
image_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


cv2.namedWindow('image')

h_min = cv2.createTrackbar('h_min','image', 0, 180, nothing)
s_min = cv2.createTrackbar('s_min','image', 0, 255, nothing)

h_max = cv2.createTrackbar('h_max','image', 0, 180, nothing)
s_max = cv2.createTrackbar('s_max','image', 0, 255, nothing)


while(1):
    h_min = cv2.getTrackbarPos('h_min', 'image')
    s_min = cv2.getTrackbarPos('s_min', 'image')

    h_max = cv2.getTrackbarPos('h_max', 'image')
    s_max = cv2.getTrackbarPos('s_max', 'image')


    mask = cv2.inRange(image_HSV, np.array([h_min,s_min,0]), np.array([h_max,s_max,255]))
    res = cv2.bitwise_and(image, image, mask=mask)

    cv2.imshow('image', res)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        cv2.imwrite("Lviv_HSV_h_min{}_s_min{}_h_max{}_s_max{}.png".format(h_min,s_min,h_max,s_max), res)
        break


cv2.destroyAllWindows()