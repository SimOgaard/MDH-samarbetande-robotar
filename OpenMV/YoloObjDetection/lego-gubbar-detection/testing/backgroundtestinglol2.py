import cv2
import numpy as np
import glob

def nothing(x):
    pass

cv2.namedWindow('filter')

cv2.createTrackbar('Min','filter',0,255,nothing)
cv2.createTrackbar('Max','filter',255,255,nothing)
cv2.createTrackbar('DILATE','filter',9,100,nothing)
cv2.createTrackbar('ERODE','filter',11,100,nothing)
cv2.createTrackbar('BLUR','filter',9,100,nothing)
# BLURHSV = 19

img = cv2.imread("Get Images/Images/gays.PNG")

# for image in glob.glob("Get Images/Images/*.PNG"):
while True:
    
    # img = cv2.cvtColor(img, cv2.COLOR_RGB2BGRA)
    
    MASK_DILATE_ITER = int(cv2.getTrackbarPos('DILATE','filter'))
    MASK_ERODE_ITER = int(cv2.getTrackbarPos('ERODE','filter'))
    BLUR = int(cv2.getTrackbarPos('BLUR','filter'))
    # Load in the image using the typical imread function using our watch_folder path, and the fileName passed in, then set the final output image to our current image for now
    
    # output = img
    # Set thresholds. Here, we are using the Hue, Saturation, Value color space model. We will be using these values to decide what values to show in the ranges using a minimum and maximum value.  THESE VALUES CAN BE PLAYED AROUND FOR DIFFERENT COLORS
    Min = int(cv2.getTrackbarPos('Min','filter'))  # Hue minimum
    Max = int(cv2.getTrackbarPos('Min','filter'))  # Saturation minimum
    # vMin = int(cv2.getTrackbarPos('vMin','min'))   # Value minimum (Also referred to as brightness)
    # hMax = int(cv2.getTrackbarPos('hMax','max')) # Hue maximum
    # sMax = int(cv2.getTrackbarPos('sMax','max')) # Saturation maximum
    # vMax = int(cv2.getTrackbarPos('vMax','max')) # Value maximum
    # # Set the minimum and max HSV values to display in the output image using numpys' array function. We need the numpy array since OpenCVs' inRange function will use those.
    # lower = np.array([hMin, sMin, vMin])
    # upper = np.array([hMax, sMax, vMax])
    # # Create HSV Image and threshold it into the proper range.

    rgb_planes = cv2.split(img)

    result_planes = []
    result_norm_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((39,39), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 71)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        result_planes.append(diff_img)
        result_norm_planes.append(norm_img)

    result = cv2.merge(result_planes)
    result_norm = cv2.merge(result_norm_planes)

    gray = cv2.cvtColor(result_norm, cv2.COLOR_BGR2GRAY) # Converting color space from BGR to HSV
    # cv2.GaussianBlur(hsv, (BLURHSV, BLURHSV), 0)
    cv2.imshow("lamao",gray)
    edges = cv2.Canny(gray, Min, Max)
    edges = cv2.dilate(edges, None)
    edges = cv2.erode(edges, None)

    contour_info = []
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    for c in contours:
        contour_info.append((
            c,
            cv2.isContourConvex(c),
            cv2.contourArea(c),
        ))
    contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
    max_contour = contour_info[0]

    mask = np.zeros(edges.shape)
    cv2.fillConvexPoly(mask, max_contour[0], (255))

    mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
    mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
    mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
    mask_stack = np.dstack([mask]*4)
    mask_stack  = mask_stack.astype('float') / 255.0 
    newimg = cv2.multiply(mask_stack, cv2.cvtColor(img, cv2.COLOR_BGR2BGRA).astype("float")/255)
    # cords = Image.fromarray(newimg.astype('uint8'), 'RGBA').getbbox()
    # newimg = newimg[cords[1]:cords[3],cords[0]:cords[2]]
    cv2.imshow("lol",newimg)
    cv2.imshow("lal",edges)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # processImage("Get Images/Images/00000003.jpg")
    k = cv2.waitKey()
    if k==27:
        break
    # elif k==-1:
    #     continue
# img = cv2.imread(image)

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