import cv2
import glob
import os

for image in glob.glob("Edit Characters/ImagesNoBackground/*.png"):
    img = cv2.imread(image)
    
    while(1):
        cv2.imshow('img',img)
        k = cv2.waitKey(33)
        if k==27:
            break
        elif k==0:
            print("[INFO] deleting {}".format(image))
            os.remove(image)
            break
        elif k!=-1:
            break
    if k ==27:
        break
    cv2.destroyAllWindows()
