import cv2
import numpy as np
import glob
from matplotlib import pyplot as plt

def nothing(x):
    pass

cv2.namedWindow('min')
cv2.namedWindow('max')
cv2.namedWindow('filter')

cv2.createTrackbar('hMin','min',0,255,nothing)
cv2.createTrackbar('sMin','min',100,255,nothing)
cv2.createTrackbar('vMin','min',0,255,nothing)
cv2.createTrackbar('hMax','max',255,255,nothing)
cv2.createTrackbar('sMax','max',255,255,nothing)
cv2.createTrackbar('vMax','max',255,255,nothing)
cv2.createTrackbar('DILATE','filter',0,100,nothing)
cv2.createTrackbar('ERODE','filter',0,100,nothing)
cv2.createTrackbar('BLUR','filter',3,100,nothing)
cv2.createTrackbar('Kernel','filter',3,100,nothing)

img = cv2.imread("Get Images/Images/xDDDD.PNG")

# b,g,r = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))
# hist = cv2.calcHist([cv2.cvtColor(img, cv2.COLOR_BGR2HSV)], [0], None, [256], [0, 256])
# plt.plot(hist)

# plt.hist(r.ravel(), 256, [0,256])
# plt.hist(g.ravel(), 256, [0,256])
# plt.hist(b.ravel(), 256, [0,256])

while True:
    
    MASK_DILATE_ITER = int(cv2.getTrackbarPos('DILATE','filter'))
    MASK_ERODE_ITER = int(cv2.getTrackbarPos('ERODE','filter'))
    BLUR = int(cv2.getTrackbarPos('BLUR','filter'))
    hMin = int(cv2.getTrackbarPos('hMin','min')) 
    sMin = int(cv2.getTrackbarPos('sMin','min')) 
    vMin = int(cv2.getTrackbarPos('vMin','min')) 
    hMax = int(cv2.getTrackbarPos('hMax','max')) 
    sMax = int(cv2.getTrackbarPos('sMax','max')) 
    vMax = int(cv2.getTrackbarPos('vMax','max')) 
    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])
    KERNEL = np.ones((int(cv2.getTrackbarPos('Kernel','filter')) ,int(cv2.getTrackbarPos('Kernel','filter'))), np.uint8)

    # rgb_planes = cv2.split(img)
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

    # cv2.imshow('shadows_out.png', result)
    # cv2.imshow('shadows_out_norm.png', result_norm)

    # gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (39,39))
    # dialated = cv2.morphologyEx(gray, cv2.MORPH_DILATE, kernel)
    # diff1 = 255-cv2.subtract(dialated, gray)

    # median = cv2.medianBlur(dialated, 71)
    # diff2 = 255- cv2.subtract(median, gray)

    # normed = cv2.normalize(diff2,None,0,255,cv2.NORM_MINMAX)

    # cv2.imshow("normed",normed)
    # cv2.imshow("diff1",diff1)
    # cv2.imshow("diff2",diff2)
    # cv2.imshow("dialated",dialated)
    # cv2.imshow("median",median)

    # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # cv2.imshow("lamao",hsv)

    # mask = cv2.inRange(hsv, lower, upper)
    # mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
    # mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
    # mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
        
    # output = cv2.bitwise_and(img, img, mask=mask)
    # *_, alpha = cv2.split(output)
    # dst = cv2.merge((output, alpha))
    # output = dst
   
    # cv2.imshow("lol",output)


    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
    mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL, iterations=2)
    mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)

    # edges = cv2.Canny(mask, 0, 255)
    # edges = cv2.dilate(edges, None)
    # edges = cv2.erode(edges, None)

    # contour_info = []
    # contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    # for c in contours:
    #     contour_info.append((
    #         c,
    #         cv2.isContourConvex(c),
    #         cv2.contourArea(c),
    #     ))

    # contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
    # max_contour = contour_info[0]

    # mask = np.zeros(edges.shape)

    # cv2.drawContours(mask, [max_contour[0]],-1, 255, -1)

    mask_stack = np.dstack([mask]*4)
    mask_stack  = mask_stack.astype('float') / 255.0 
    newimg = cv2.multiply(mask_stack, cv2.cvtColor(img, cv2.COLOR_BGR2BGRA).astype("float")/255)

    # cv2.imshow("newimg",cv2.pyrDown(newimg))
    cv2.imshow("newimg",cv2.pyrDown(newimg))
    cv2.imshow("hsv",cv2.pyrDown(hsv))
    k = cv2.waitKey()
    if k==27:
        break

cv2.destroyAllWindows()



# import cv2
# import numpy as np

# #== Parameters =======================================================================
# BLUR = 21
# CANNY_THRESH_1 = 10
# CANNY_THRESH_2 = 200
# MASK_DILATE_ITER = 10
# MASK_ERODE_ITER = 10
# MASK_COLOR = (0.0,0.0,1.0) # In BGR format

# CANNY_THRESH_1 = 0
# CANNY_THRESH_2 = 80
# MASK_COLOR = (0,0,0)

# hMin = 0
# sMin = 4
# vMin = 0
# hMax = 255
# sMax = 255
# vMax = 255
# MASK_DILATE_ITER = 0
# MASK_ERODE_ITER = 2
# BLUR = 3
# KERNEL = np.ones((5,5), np.uint8)

# lower = np.array([hMin, sMin, vMin])
# upper = np.array([hMax, sMax, vMax])


# #== Processing =======================================================================

# #-- Read image -----------------------------------------------------------------------
# img = cv2.imread('Get Images/Images/00000003.jpg')
# # img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
# hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# edges = cv2.inRange(hsv, lower, upper)

# #-- Edge detection -------------------------------------------------------------------
# # edges = cv2.Canny(gray, CANNY_THRESH_1, CANNY_THRESH_2)
# edges = cv2.dilate(edges, None)
# edges = cv2.erode(edges, None)

# cv2.imshow('img', edges)                                   # Display
# cv2.waitKey()

# #-- Find contours in edges, sort by area ---------------------------------------------
# contour_info = []
# contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
# # Previously, for a previous version of cv2, this line was: 
# #  contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
# # Thanks to notes from commenters, I've updated the code but left this note
# for c in contours:
#     contour_info.append((
#         c,
#         cv2.isContourConvex(c),
#         cv2.contourArea(c),
#     ))
# contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
# max_contour = contour_info[0]

# #-- Create empty mask, draw filled polygon on it corresponding to largest contour ----
# # Mask is black, polygon is white
# mask = np.zeros(edges.shape)
# cv2.fillConvexPoly(mask, max_contour[0], (255))

# cv2.imshow('img', mask)                                   # Display
# cv2.waitKey()

# #-- Smooth mask, then blur it --------------------------------------------------------
# mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
# mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
# mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
# mask_stack = np.dstack([mask]*3)    # Create 3-channel alpha mask

# #-- Blend masked img into MASK_COLOR background --------------------------------------
# mask_stack  = mask_stack.astype('float32') / 255.0          # Use float matrices, 
# img         = img.astype('float32') / 255.0                 #  for easy blending

# masked = (mask_stack * img) + ((1-mask_stack) * MASK_COLOR) # Blend
# masked = (masked * 255).astype('uint8')                     # Convert back to 8-bit 

# cv2.imshow('img', masked)                                   # Display
# cv2.waitKey()


# # cv2.imshow('img', edges)                                   # Display
# # cv2.waitKey()
# # #-- Find contours in edges, sort by area ---------------------------------------------
# # contour_info = []
# # contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
# # # Previously, for a previous version of cv2, this line was: 
# # #  contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
# # # Thanks to notes from commenters, I've updated the code but left this note
# # for c in contours:
# #     contour_info.append((
# #         c,
# #         cv2.isContourConvex(c),
# #         cv2.contourArea(c),
# #     ))
# # contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
# # max_contour = contour_info[0]

# # #-- Create empty mask, draw filled polygon on it corresponding to largest contour ----
# # # Mask is black, polygon is white
# # mask = np.zeros(edges.shape)
# # cv2.fillConvexPoly(mask, max_contour[0], (255))

# # cv2.imshow('img', mask)                                   # Display
# # cv2.waitKey()

# # #-- Smooth mask, then blur it --------------------------------------------------------
# # mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
# # mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
# # mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
# # mask_stack = np.dstack([mask]*3)    # Create 3-channel alpha mask

# # cv2.imshow('img', mask)                                   # Display
# # cv2.waitKey()
# # cv2.imshow('img', mask_stack)                                   # Display
# # cv2.waitKey()
# # #-- Blend masked img into MASK_COLOR background --------------------------------------
# # mask_stack  = mask_stack.astype('float32') / 255.0          # Use float matrices, 
# # img         = img.astype('float32') / 255.0                 #  for easy blending

# # masked = (mask_stack * img) + ((1-mask_stack) * MASK_COLOR) # Blend
# # masked = (masked * 255).astype('uint8')                     # Convert back to 8-bit 

# # cv2.imshow('img', masked)                                   # Display
# # cv2.waitKey()

# # #cv2.imwrite('C:/Temp/person-masked.jpg', masked)           # Save