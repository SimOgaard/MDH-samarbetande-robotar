import cv2
import numpy as np
from PIL import Image
import glob
import os

MASK_COLOR = (0,0,0,0)

# hMin = 0
# sMin = 46
# vMin = 0
# hMax = 255
# sMax = 255
# vMax = 160
# MASK_DILATE_ITER = 12
# MASK_ERODE_ITER = 14
# BLUR = 9
# KERNEL = np.ones((5,5), np.uint8)

Min = 115
Max = 0
MASK_DILATE_ITER = 9
MASK_ERODE_ITER = 11
BLUR = 9
KERNEL = np.ones((5,5), np.uint8)

skipamount = 1

for video in glob.glob("Get Images/Video/*.mp4"):
    if not os.path.exists("Edit Characters/FramesNoBackground/"+video[17:-4]):
        os.makedirs("Edit Characters/FramesNoBackground/"+video[17:-4])
    else:
        continue
    cap = cv2.VideoCapture(video)
    total = 0
    skip = 0
    while(cap.isOpened()):
        # try:
        ret, frame = cap.read()
        skip += 1 
        if skip <= skipamount:
            continue
        skip = 0

        if not ret:
            break


        # rgb_planes = cv2.split(frame)

        # result_planes = []
        # result_norm_planes = []
        # for plane in rgb_planes:
        #     dilated_img = cv2.dilate(plane, np.ones((39,39), np.uint8))
        #     bg_img = cv2.medianBlur(dilated_img, 71)
        #     diff_img = 255 - cv2.absdiff(plane, bg_img)
        #     norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        #     result_planes.append(diff_img)
        #     result_norm_planes.append(norm_img)

        # result = cv2.merge(result_planes)
        # result_norm = cv2.merge(result_norm_planes)




        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (39,39))
        dialated = cv2.morphologyEx(gray, cv2.MORPH_DILATE, kernel)
        diff1 = 255-cv2.subtract(dialated, gray)

        median = cv2.medianBlur(dialated, 71)
        diff2 = 255- cv2.subtract(median, gray)

        normed = cv2.normalize(diff2,None,0,255,cv2.NORM_MINMAX)


        edges = cv2.Canny(normed, Min, Max)
        # edges = cv2.dilate(edges, None)
        # edges = cv2.erode(edges, None)
        edges = cv2.dilate(edges, None, iterations=MASK_DILATE_ITER)
        edges = cv2.erode(edges, None, iterations=MASK_ERODE_ITER)
        # mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)

        # mask = cv2.inRange(gray, CANNY_THRESH_1, CANNY_THRESH_2)

        #-- Find contours in edges, sort by area ---------------------------------------------
        contour_info = []
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        # Previously, for a previous version of cv2, this line was: 
        #  contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        # Thanks to notes from commenters, I've updated the code but left this note
        for c in contours:
            contour_info.append((
                c,
                cv2.isContourConvex(c),
                cv2.contourArea(c),
            ))
        contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
        max_contour = contour_info[0]

        #-- Create empty mask, draw filled polygon on it corresponding to largest contour ----
        # Mask is black, polygon is white
        mask = np.zeros(edges.shape)
        cv2.fillConvexPoly(mask, max_contour[0], (255))

        #-- Smooth mask, then blur it --------------------------------------------------------
        # mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
        mask = cv2.erode(mask, None)
        mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
        # mask_stack = np.dstack([mask]*3)    # Create 3-channel alpha mask

        mask_stack = np.dstack([mask]*4)
        mask_stack  = mask_stack.astype('float') / 255.0 
        newimg = cv2.multiply(mask_stack, cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA).astype("float")/255)
        cords = Image.fromarray(newimg.astype('uint8'), 'RGBA').getbbox()
        # newimg = newimg[cords[1]:cords[3],cords[0]:cords[2]]            # cv2.imshow("hsv",cv2.pyrDown(hsv))
        # cv2.imshow("edges", cv2.pyrDown(edges))
        # cv2.imshow("frame", cv2.pyrDown(frame))
        # cv2.imshow("mask", cv2.pyrDown(mask))
        # cv2.imshow("newimg", newimg)
        cv2.waitKey()
        cv2.destroyAllWindows()

        cv2.imwrite("Edit Characters/FramesNoBackground/"+video[17:-4]+"/"+"{}.png".format(str(total).zfill(8)), (newimg * 255).astype('uint8'))
        total+=1
        # except:
        #     pass
    cap.release()