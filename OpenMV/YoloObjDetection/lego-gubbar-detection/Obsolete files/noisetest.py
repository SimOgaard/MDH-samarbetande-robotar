# # import numpy as np
# # import os
# # import cv2
# # def noisy(noise_typ,image):
# #     if noise_typ == "gauss":
# #         row,col,ch= image.shape
# #         mean = 0
# #         var = 0.1
# #         sigma = var**0.5
# #         gauss = np.random.normal(mean,sigma,(row,col,ch))
# #         gauss = gauss.reshape(row,col,ch)
# #         noisy = image + gauss
# #         return noisy
# #     elif noise_typ == "s&p":
# #         row,col,ch = image.shape
# #         s_vs_p = 0.5
# #         amount = 0.004
# #         out = np.copy(image)
# #         # Salt mode
# #         num_salt = np.ceil(amount * image.size * s_vs_p)
# #         coords = [np.random.randint(0, i - 1, int(num_salt))
# #                 for i in image.shape]
# #         out[coords] = 1

# #         # Pepper mode
# #         num_pepper = np.ceil(amount* image.size * (1. - s_vs_p))
# #         coords = [np.random.randint(0, i - 1, int(num_pepper))
# #                 for i in image.shape]
# #         out[coords] = 0
# #         return out
# #     elif noise_typ == "poisson":
# #         vals = len(np.unique(image))
# #         vals = 2 ** np.ceil(np.log2(vals))
# #         noisy = np.random.poisson(image * vals) / float(vals)
# #         return noisy
# #     elif noise_typ =="speckle":
# #         row,col,ch = image.shape
# #         gauss = np.random.randn(row,col,ch)
# #         gauss = gauss.reshape(row,col,ch)        
# #         noisy = image + image * gauss
# #         return noisy

# # cv2.imshow("s&p",noisy("speckle",cv2.imread("lena.jpg")))
# # cv2.imshow("original", cv2.imread("lena.jpg"))
# # cv2.waitKey(0)
# # # from __future__ import print_function
# # # from builtins import input
# # # import cv2 as cv
# # # import numpy as np
# # # import argparse
# # # # Read image given by user
# # # parser = argparse.ArgumentParser(description='Code for Changing the contrast and brightness of an image! tutorial.')
# # # parser.add_argument('--input', help='Path to input image.', default='lena.jpg')
# # # args = parser.parse_args()
# # # image = cv.imread(cv.samples.findFile(args.input))
# # # if image is None:
# # #     print('Could not open or find the image: ', args.input)
# # #     exit(0)
# # # new_image = np.zeros(image.shape, image.dtype)
# # # alpha = 1.0 # Simple contrast control
# # # beta = 0    # Simple brightness control
# # # # Initialize values
# # # print(' Basic Linear Transforms ')
# # # print('-------------------------')
# # # try:
# # #     alpha = float(input('* Enter the alpha value [1.0-3.0]: '))
# # #     beta = int(input('* Enter the beta value [0-100]: '))
# # # except ValueError:
# # #     print('Error, not a number')
# # # # Do the operation new_image(i,j) = alpha*image(i,j) + beta
# # # # Instead of these 'for' loops we could have used simply:
# # # # new_image = cv.convertScaleAbs(image, alpha=alpha, beta=beta)
# # # # but we wanted to show you how to access the pixels :)
# # # for y in range(image.shape[0]):
# # #     for x in range(image.shape[1]):
# # #         for c in range(image.shape[2]):
# # #             new_image[y,x,c] = np.clip(alpha*image[y,x,c] + beta, 0, 255)
# # # cv.imshow('Original Image', image)
# # # cv.imshow('New Image', new_image)
# # # # Wait until user press some key
# # # cv.waitKey()

# def intersects(self, other):
#     return not (self.top_right.x < other.bottom_left.x or self.bottom_left.x > other.top_right.x or self.top_right.y < other.bottom_left.y or self.bottom_left.y > other.top_right.y)

# r1=((1,1), (2,2))
# r3=((1.5,0), (1.7,3))
# print(intersects(r1,r3))

import cv2
import numpy as np
from skimage.util import random_noise
 
# Load the image
img = cv2.imread("Get Images/lena.jpg")
 
# Add salt-and-pepper noise to the image.
noise_img = random_noise(img, mode='s&p',amount=0.001)
 
# The above function returns a floating-point image
# on the range [0, 1], thus we changed it to 'uint8'
# and from [0,255]
noise_img = np.array(255*noise_img, dtype = 'uint8')
 
# Display the noise image
cv2.imshow('blur',noise_img)
cv2.waitKey(0)

##################################################

# Generate Gaussian noise
gauss = np.random.normal(0,0.2,img.size)
gauss = gauss.reshape(img.shape[0],img.shape[1],img.shape[2]).astype('uint8')
# Add the Gaussian noise to the image
img_gauss = cv2.add(img,gauss)
# Display the image
cv2.imshow('a',img_gauss)
cv2.waitKey(0)

#####################################################
 
gauss = np.random.normal(0,0.2,img.size)
gauss = gauss.reshape(img.shape[0],img.shape[1],img.shape[2]).astype('uint8')
noise = img + img * gauss
 
cv2.imshow('a',noise)
cv2.waitKey(0)