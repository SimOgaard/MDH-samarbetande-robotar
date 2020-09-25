import cv2
import numpy as np
from PIL import Image
import glob

for video in glob.glob("Get Images/VideoDone/*.mp4"):
    cap = cv2.VideoCapture(video)
    total = 0

    ret, img = cap.read()
    if not ret:
        break

    # img = cv2.imread("Capture.PNG")

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Edge detection 
    edges = cv2.Canny(gray, 150, 255)
    edges = cv2.dilate(edges, None, iterations=4)
    edges = cv2.erode(edges, None, iterations=4)
    cv2.imshow('edge', edges)

    # Find contours in edges, sort by area 
    contour_info = []
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        contour_info.append((
            c,
            cv2.isContourConvex(c),
            cv2.contourArea(c),
        ))
    contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
    max_contour = contour_info[0]

    # Create empty mask and flood fill
    mask = np.zeros(edges.shape)
    for c in contour_info:
        cv2.fillConvexPoly(mask, c[0], (255))

    # Smooth mask and blur it
    # mask = cv2.dilate(mask, None, iterations=10)
    # mask = cv2.erode(mask, None, iterations=10)
    # mask = cv2.GaussianBlur(mask, (3, 3), 0)

    cv2.imshow('mask', mask)

    # Create 3-channel alpha mask
    # mask_stack = np.dstack([mask]*3)

    mask_stack = np.dstack([mask]*4)
    mask_stack  = mask_stack.astype('float') / 255.0
    newimg = cv2.multiply(mask_stack, cv2.cvtColor(img, cv2.COLOR_BGR2BGRA).astype("float")/255)
    cords = Image.fromarray(newimg.astype('uint8'), 'RGBA').getbbox()
    newimg = newimg[cords[1]:cords[3],cords[0]:cords[2]]


    cv2.imshow('mask_s', mask_stack)

    # Blend mask and foreground image
    # mask_stack  = mask_stack.astype('float32') / 255.0
    # img         = img.astype('float32') / 255.0
    # masked = (mask_stack * img) + ((1-mask_stack) * (1.0,1.0,1.0))
    # masked = (masked * 255).astype('uint8')

    # Make the background transparent by adding 4th alpha channel
    # tmp = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    # _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
    # b, g, r = cv2.split(masked)
    # rgba = [b,g,r, alpha]
    # dst = cv2.merge(rgba,4)

    # Display
    cv2.imwrite("Edit Characters/FramesNoBackground/"+video[17:-4]+"_{}.png".format(str(total).zfill(8)), (newimg * 255).astype('uint8'))
    total+=1
