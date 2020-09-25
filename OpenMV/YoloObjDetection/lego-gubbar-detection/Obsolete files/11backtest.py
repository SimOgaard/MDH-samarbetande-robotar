import cv2
import numpy as np

img = cv2.imread("IMG_1982.PNG")
gray = cv2.imread("IMG_1982.PNG", cv2.IMREAD_GRAYSCALE)

img = cv2.pyrDown(img)
gray = cv2.pyrDown(gray)
img = cv2.pyrDown(img)
gray = cv2.pyrDown(gray)

cv2.imshow("gray", gray)

gray=cv2.bilateralFilter(gray,11,17,17)
edge=cv2.Canny(gray,30,200)
cnts, _ = cv2.findContours(edge.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnt = sorted(cnts, key = cv2.contourArea)[-1]


# gray = cv2.imread("IMG_1982.PNG", cv2.IMREAD_GRAYSCALE)
# img = cv2.imread("IMG_1982.PNG")
# # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
# gray=cv2.bilateralFilter(gray,11,17,17)

# cv2.imshow(gray, "gray")

# edge=cv2.Canny(gray,30,200)
# cnts, _ = cv2.findContours(edge.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cnt = sorted(cnts, key = cv2.contourArea)[-1]

cnt=cnt.astype(np.int)
        
alphachannel=np.zeros(img.shape[:2],dtype=np.uint8)

cv2.drawContours(alphachannel,cnt,0,255,-1)

cv2.imshow("lamao", alphachannel)
cv2.waitKey()

# alphachannel=cv2.bitwise_and(alphachannel,alphamask)
img[:,:,3]=alphachannel

