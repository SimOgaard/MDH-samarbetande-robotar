import cv2
img = cv2.imread("00000000.JPEG")
cv2.rectangle(img, (95, 199), (202, 285), (255,0,0), 1)
cv2.rectangle(img, (173, 59), (239, 126), (255,0,0), 1)
cv2.rectangle(img, (168, 13), (199, 36), (255,0,0), 1)
cv2.imshow("img", img)
# 95</xmin><ymin>199</ymin><xmax>202</xmax><ymax>285
# 173</xmin><ymin>59</ymin><xmax>239</xmax><ymax>126
# 168</xmin><ymin>13</ymin><xmax>199</xmax><ymax>36
cv2.waitKey()