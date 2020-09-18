import cv2
import numpy as np
import glob

def nothing(x):
    pass

cv2.namedWindow('min')
cv2.namedWindow('max')
cv2.namedWindow('filter')

cv2.createTrackbar('hMin','min',0,255,nothing)
cv2.createTrackbar('sMin','min',20,255,nothing)
cv2.createTrackbar('vMin','min',0,255,nothing)
cv2.createTrackbar('hMax','max',120,255,nothing)
cv2.createTrackbar('sMax','max',255,255,nothing)
cv2.createTrackbar('vMax','max',160,255,nothing)
cv2.createTrackbar('DILATE','filter',8,100,nothing)
cv2.createTrackbar('ERODE','filter',10,100,nothing)
cv2.createTrackbar('BLUR','filter',3,100,nothing)
# BLURHSV = 19

img = cv2.imread("Get Images/Images/00000003.jpg")

for image in glob.glob("Get Images/Images/*.PNG"):
    while True:
        
        img = cv2.imread(image)
        
        MASK_DILATE_ITER = int(cv2.getTrackbarPos('DILATE','filter'))
        MASK_ERODE_ITER = int(cv2.getTrackbarPos('ERODE','filter'))
        BLUR = int(cv2.getTrackbarPos('BLUR','filter'))
        # Load in the image using the typical imread function using our watch_folder path, and the fileName passed in, then set the final output image to our current image for now
        
        output = img
        # Set thresholds. Here, we are using the Hue, Saturation, Value color space model. We will be using these values to decide what values to show in the ranges using a minimum and maximum value.  THESE VALUES CAN BE PLAYED AROUND FOR DIFFERENT COLORS
        hMin = int(cv2.getTrackbarPos('hMin','min'))  # Hue minimum
        sMin = int(cv2.getTrackbarPos('sMin','min'))  # Saturation minimum
        vMin = int(cv2.getTrackbarPos('vMin','min'))   # Value minimum (Also referred to as brightness)
        hMax = int(cv2.getTrackbarPos('hMax','max')) # Hue maximum
        sMax = int(cv2.getTrackbarPos('sMax','max')) # Saturation maximum
        vMax = int(cv2.getTrackbarPos('vMax','max')) # Value maximum
        # Set the minimum and max HSV values to display in the output image using numpys' array function. We need the numpy array since OpenCVs' inRange function will use those.
        lower = np.array([hMin, sMin, vMin])
        upper = np.array([hMax, sMax, vMax])
        # Create HSV Image and threshold it into the proper range.
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) # Converting color space from BGR to HSV
        # cv2.GaussianBlur(hsv, (BLURHSV, BLURHSV), 0)
        cv2.imshow("lamao",hsv)
        mask = cv2.inRange(hsv, lower, upper) # Create a mask based on the lower and upper range, using the new HSV image
        mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
        mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
        mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
            
        # Create the output image, using the mask created above. This will perform the removal of all unneeded colors, but will keep a black background.
        output = cv2.bitwise_and(img, img, mask=mask)
        # Add an alpha channel, and update the output image variable
        *_, alpha = cv2.split(output)
        dst = cv2.merge((output, alpha))
        output = dst
        # Resize the image to 512, 512 (This can be put into a variable for more flexibility), and update the output image variable.
        #   dim = (512, 512)
        #   output = cv2.resize(output, dim)
        # Generate a random file name using a mini helper function called randomString to write the image data to, and then save it in the processed_folder path, using the generated filename.
        #   cv2.imwrite(processed_folder + "/" + fileName, output)
        cv2.imshow("lol",output)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # processImage("Get Images/Images/00000003.jpg")
        k = cv2.waitKey()
        if k==27:
            break
        elif k==-1:
            continue
    img = cv2.imread(image)

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