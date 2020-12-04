import cv2
img = cv2.imread("rgb.png")

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

cv2.imwrite("hsv.png", hsv)