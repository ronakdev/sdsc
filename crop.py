import cv2, numpy as np, sys, math

def isCloseTo(a,b,error):
    return abs(a - b) <= error

def cropMask(mask):
    gray = mask.copy()
    final = gray.copy()
    edges = cv2.Canny(gray,50,150,apertureSize = 3)
    #cv2.imwrite('edges-50-150.jpg',edges)
    minLineLength=100
    lines = cv2.HoughLinesP(image=edges,rho=1,theta=np.pi/180, threshold=100,lines=np.array([]), minLineLength=minLineLength,maxLineGap=80)

    a,b,c = lines.shape
    min = [sys.maxsize, sys.maxsize]
    max = [-sys.maxsize - 1, -sys.maxsize - 1]
    bestLines = []
    for i in range(a):
        cv2.line(gray, (lines[i][0][0], lines[i][0][1]), (lines[i][0][2], lines[i][0][3]), (0, 0, 255), 3, cv2.LINE_AA)
        #cv2.imwrite('houghlines5.jpg',gray)

        #print("Line #" + str(i))
        #print("Coord1: x: " + str(lines[i][0][0]) + " y: " + str(lines[i][0][1]))
        #print("Coord2: x: " + str(lines[i][0][2]) + " y: " + str(lines[i][0][3]))
        #print("\n")
        min[0] = lines[i][0][0] if (min[0] > lines[i][0][0]) else min[0]
        max[0] = lines[i][0][0] if (max[0] < lines[i][0][0]) else max[0]

        min[1] = lines[i][0][1] if (min[1] > lines[i][0][1]) else min[1]
        max[1] = lines[i][0][1] if (max[1] < lines[i][0][1]) else max[1]

        min[0] = lines[i][0][2] if (min[0] > lines[i][0][2]) else min[0]
        max[0] = lines[i][0][2] if (max[0] < lines[i][0][2]) else max[0]

        min[1] = lines[i][0][3] if (min[1] > lines[i][0][3]) else min[1]
        max[1] = lines[i][0][3] if (max[1] < lines[i][0][3]) else max[1]

        #print(len(lines))
        #print('min: ' + str(min))
        #print("max: " + str(max))
        #m = (max[1] - min[1]) / (max[0] - min[0])
        m = (lines[i][0][3] - lines[i][0][1]) / (lines[i][0][2] - lines[i][0][0])
        if isCloseTo(m, 0, 0.01):
            bestLines.append(lines[i])

        #print("slope: " + str(m))
    #cv2.imshow("Final", gray)

    min = [sys.maxsize, sys.maxsize]
    max = [-sys.maxsize - 1, -sys.maxsize - 1]
    for l in bestLines:
        cv2.line(final, (l[0][0], l[0][1]), (l[0][2], l[0][3]), (0, 0, 255), 3, cv2.LINE_AA)
        min[0] = l[0][0] if (min[0] > l[0][0]) else min[0]
        max[0] = l[0][0] if (max[0] < l[0][0]) else max[0]

        min[1] = l[0][1] if (min[1] > l[0][1]) else min[1]
        max[1] = l[0][1] if (max[1] < l[0][1]) else max[1]

        min[0] = l[0][2] if (min[0] > l[0][2]) else min[0]
        max[0] = l[0][2] if (max[0] < l[0][2]) else max[0]

        min[1] = l[0][3] if (min[1] > l[0][3]) else min[1]
        max[1] = l[0][3] if (max[1] < l[0][3]) else max[1]

    #print('min: ' + str(min))
    #print("max: " + str(max))
    cropped = mask[min[1]:max[1],min[0]:max[0]]
    #cv2.imshow("finale", final)
    #cv2.imshow('cropped', cropped)
    #cv2.waitKey(0)
    return cropped
