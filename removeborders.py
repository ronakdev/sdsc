import sys
import cv2 as cv
import numpy as np


def cv_size(img):
    return tuple(img.shape[1::-1])

def contourImage(img):
    return cv.findContours(img, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

def thresh(img, min, max):
    a, lower = cv.threshold(img, min, 255, cv.THRESH_BINARY)
    b, upper = cv.threshold(img, max, 255, cv.THRESH_BINARY_INV)
    return (lower & upper)

def findBiggestArc(contours, img):
    maxArea = 0
    maxIndex = -1
    maxLen = 0
    currentIndex = 0
    for contour in contours:
        if (cv.isContourConvex(contour)):
            epsilon = 0.1 * cv.arcLength(contour, True)
            approx = cv.approxPolyDP(contour, epsilon, True)
            if (len(approx) == 4):
                (x, y, w, h) = cv.boundingRect(approx)

                rectArea = cv.contourArea(contour)
                maxArea = rectArea if (rectArea > maxArea) else maxArea
                maxIndex = currentIndex if (rectArea > maxArea) else maxIndex
        else:
            length = cv.arcLength(contour, False)
            if (length > maxLen):
                maxLen = length
                maxIndex = currentIndex
            #maxIndex = currentIndex if (length > maxLen) else maxIndex
        currentIndex += 1

    return (maxIndex, maxLen)
imagepath = sys.argv[1]

# time to remove the border
img = cv.imread(imagepath)
level1 = int(sys.argv[2])
level2 = int(sys.argv[3])
img = cv.GaussianBlur(img, (level1,level1), level2, level2)
cv.imshow("blur", img)

cvted = cv.cvtColor(img, cv.COLOR_BGR2HSV)
seperated = cv.split(cvted)
hue = seperated[0]
edges = cv.Canny(seperated[2], 0, 25)
cv.imshow("edges",edges)


_, contours, hierarchy = cv.findContours(edges,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
areas = [cv.contourArea(c) for c in contours]
max_index = np.argmax(areas)
cnt=contours[max_index]

print("largest area: " + str(areas[max_index]))

index, len = findBiggestArc(contours, img)
print("largest len: " + str(len))
#contourMask = cv.zeros(cv_size(img), cv.8UC1)
cv.drawContours(img, contours, index, (0,255,0), 3)
cv.imshow("done", img)
cv.waitKey(0)

'''
mask = np.zeros_like(img) # Create mask where white is what we want, black otherwise
cv.drawContours(mask, contours, max_index, 255, -1) # Draw filled contour in mask
out = np.zeros_like(img) # Extract out the object and place into output image
out[mask == 255] = img[mask == 255]

# Show the output image
cv.imshow('Output', out)
cv.imshow('Original', img)
cv.waitKey(0)
cv.destroyAllWindows()
'''
