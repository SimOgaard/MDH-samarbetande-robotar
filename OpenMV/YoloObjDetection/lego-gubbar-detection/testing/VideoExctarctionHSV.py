import cv2
import numpy as np
from PIL import Image
import glob

MASK_COLOR = (0,0,0,0)

hMin = 0
sMin = 116
vMin = 0
hMax = 255
sMax = 255
vMax = 255
MASK_DILATE_ITER = 9
MASK_ERODE_ITER = 11
BLUR = 9
KERNEL = np.ones((5,5), np.uint8)

lower = np.array([hMin, sMin, vMin])
upper = np.array([hMax, sMax, vMax])

total = 0

# for image in glob.glob("Get Images/Images/*.jpg"):
#     try:
#         img = cv2.cvtColor(cv2.imread(image), cv2.COLOR_RGB2RGBA)
#         hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

#         mask = cv2.inRange(hsv, lower, upper)
#         mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
#         mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
#         mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL, iterations=2)
#         mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)

#         # ta masken och tracea den sätt ihop gaps och fyll i den till 100%
        
#         mask_stack = np.dstack([mask]*4)
#         mask_stack  = mask_stack.astype('float') / 255.0 
#         newimg = cv2.multiply(mask_stack, cv2.cvtColor(img, cv2.COLOR_BGR2BGRA).astype("float")/255)
#         cords = Image.fromarray(newimg.astype('uint8'), 'RGBA').getbbox()
#         newimg = newimg[cords[1]:cords[3],cords[0]:cords[2]]

#         cv2.imwrite("Edit Characters/ImagesNoBackground/"+image[-12:-3]+"png", (newimg * 255).astype('uint8'))

#         cv2.imshow('croppedimg', newimg)
#         cv2.imshow('mask_stack', mask_stack)
#         k = cv2.waitKey()
#         if k==27:
#             break
#     except Exception as e:
#         print(e)
#         continue

for video in glob.glob("Get Images/Video/*.mp4"):
    cap = cv2.VideoCapture(video)
    while(cap.isOpened()):
        _, frame = cap.read()

        img = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
        mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL, iterations=2)
        mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)

        # ta masken och tracea den sätt ihop gaps och fyll i den till 100%
        
        mask_stack = np.dstack([mask]*4)
        mask_stack  = mask_stack.astype('float') / 255.0 
        newimg = cv2.multiply(mask_stack, cv2.cvtColor(img, cv2.COLOR_BGR2BGRA).astype("float")/255)
        cords = Image.fromarray(newimg.astype('uint8'), 'RGBA').getbbox()
        newimg = newimg[cords[1]:cords[3],cords[0]:cords[2]]

        # cv2.imwrite("Edit Characters/ImagesNoBackground/"+image[-12:-3]+"png", (newimg * 255).astype('uint8'))

        # cv2.imshow('croppedimg', newimg)
        # cv2.imshow('mask_stack', mask_stack)

        cv2.imwrite("Edit Characters/FramesNoBackground/"+"{}.png".format(str(total).zfill(8)), (newimg * 255).astype('uint8'))
        total+=1
    
    cap.release()
    cv2.destroyAllWindows()