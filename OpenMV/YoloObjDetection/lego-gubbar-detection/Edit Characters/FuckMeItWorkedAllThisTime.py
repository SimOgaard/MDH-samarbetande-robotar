# ANVÄND LILA BAKGRUND

import cv2
import numpy as np
from PIL import Image
import glob

AMOUNT=0
REP=0

MASK_COLOR = (0,0,0,0)

hMin = 0
sMin = 130
vMin = 0
hMax = 255
sMax = 255
vMax = 150
MASK_DILATE_ITER = 4
MASK_ERODE_ITER = 4
BLUR = 9
KERNEL = np.ones((9,9), np.uint8)

lower = np.array([hMin, sMin, vMin])
upper = np.array([hMax, sMax, vMax])

img = cv2.imread("Obsolete files/20200925_140958.PNG") # 20200925_131954, 20200925_132439
img = cv2.pyrDown(img)

# C:\Users\s8simoga\Documents\GitHub\Livindead3\MDH-samarbetande-robotar\OpenMV\YoloObjDetection\lego-gubbar-detection\Obsolete files\20200925_132439.png

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

mask = cv2.inRange(hsv, lower, upper)
mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL, iterations=2)
mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)

edges = cv2.Canny(mask, 0, 255)
edges = cv2.dilate(edges, None)
edges = cv2.erode(edges, None)

contour_info = []
contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

for c in contours:
    AMOUNT += cv2.contourArea(c)
    REP += 1
    print(cv2.contourArea(c))
    contour_info.append((
        c,
        cv2.isContourConvex(c),
        cv2.contourArea(c),
    ))
    
total = 0

skip = True

for contour in contour_info:
    if skip:
        skip = False
        continue
    mask = np.zeros(edges.shape)
    cv2.drawContours(mask, [contour[0]],-1, 255, -1)

    mask_stack = np.dstack([mask]*4)
    mask_stack  = mask_stack.astype('float') / 255.0 
    newimg = cv2.multiply(mask_stack, cv2.cvtColor(img, cv2.COLOR_BGR2BGRA).astype("float")/255)
    cords = Image.fromarray(newimg.astype('uint8'), 'RGBA').getbbox()
    newimg = newimg[cords[1]:cords[3],cords[0]:cords[2]]

    # cv2.imshow("hsv",cv2.pyrDown(hsv))
    # cv2.imshow("edges", cv2.pyrDown(edges))
    # cv2.imshow("img", cv2.pyrDown(img))
    # cv2.imshow("mask", cv2.pyrDown(mask))
    # cv2.imshow("newimg", cv2.pyrUp(cv2.pyrUp(newimg)))
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    cv2.imwrite("Edit Characters/FramesNoBackground/"+"{}.png".format(str(total).zfill(8)), (newimg * 255).astype('uint8'))
    total+=1
    skip = True

print("lol")
print (AMOUNT/REP)