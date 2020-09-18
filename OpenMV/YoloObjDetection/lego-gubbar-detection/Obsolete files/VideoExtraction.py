import cv2
import glob
import numpy as np
from PIL import Image
import os

BLUR = 3
CANNY_THRESH_1 = 90
CANNY_THRESH_2 = 255
MASK_DILATE_ITER = 9
MASK_ERODE_ITER = 11
MASK_COLOR = (0.0,0.0,0.0)

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
        try:
            ret, frame = cap.read()
            skip += 1 
            if skip <= skipamount:
                continue
            skip = 0

            if not ret:
                break

            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, CANNY_THRESH_1, CANNY_THRESH_2)
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
            newimg = cv2.multiply(mask_stack, cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA).astype("float")/255)
            cords = Image.fromarray(newimg.astype('uint8'), 'RGBA').getbbox()
            newimg = newimg[cords[1]:cords[3],cords[0]:cords[2]]
            cv2.imwrite("Edit Characters/FramesNoBackground/"+video[17:-4]+"/"+"{}.png".format(str(total).zfill(8)), (newimg * 255).astype('uint8'))
            total+=1
        except:
            pass
    cap.release()
            # cv2.imwrite("Edit Characters/FramesNoBackground/"+"{}.png".format(str(total).zfill(8)), (newimg * 255).astype('uint8'))
            # total+=1
            # mask_stack = np.dstack([mask]*3)
            # mask_stack  = mask_stack.astype('float32') / 255.0          # Use float matrices, 
            # newimg         = frame.astype('float32') / 255.0                 #  for easy blending

            # masked = (mask_stack * newimg) + ((1-mask_stack) * MASK_COLOR) # Blend
            # masked = (masked * 255).astype('uint8')                     # Convert back to 8-bit 

            # cv2.imshow('img', masked)                                   # Display
            # cv2.waitKey()


    # cap.release()
    # cv2.destroyAllWindows()

