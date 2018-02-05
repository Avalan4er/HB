import cv2
import numpy


def nothing(x):
    pass


def find_red_creeps(screenshot):
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    cv2.namedWindow('image')

    # create trackbars for color change
    #cv2.createTrackbar('Low1H', 'image', 0, 255, nothing)
    #cv2.createTrackbar('Low1S', 'image', 70, 255, nothing)
    #cv2.createTrackbar('Low1V', 'image', 150, 255, nothing)

    #cv2.createTrackbar('Low2H', 'image', 10, 255, nothing)
    #cv2.createTrackbar('Low2S', 'image', 255, 255, nothing)
    #cv2.createTrackbar('Low2V', 'image', 240, 255, nothing)

    #cv2.createTrackbar('High1H', 'image', 170, 255, nothing)
    #cv2.createTrackbar('High1S', 'image', 700, 255, nothing)
    #cv2.createTrackbar('High1V', 'image', 150, 255, nothing)

    #cv2.createTrackbar('High2H', 'image', 180, 255, nothing)
    #cv2.createTrackbar('High2S', 'image', 255, 255, nothing)
    #cv2.createTrackbar('High2V', 'image', 240, 255, nothing)

    while 1:
        # get current positions of four trackbars
        l1h = cv2.getTrackbarPos('Low1H', 'image')
        l1s = cv2.getTrackbarPos('Low1S', 'image')
        l1v = cv2.getTrackbarPos('Low1V', 'image')

        l2h = cv2.getTrackbarPos('Low2H', 'image')
        l2s = cv2.getTrackbarPos('Low2S', 'image')
        l2v = cv2.getTrackbarPos('Low2V', 'image')

        h1h = cv2.getTrackbarPos('High1H', 'image')
        h1s = cv2.getTrackbarPos('High1S', 'image')
        h1v = cv2.getTrackbarPos('High1V', 'image')

        h2h = cv2.getTrackbarPos('High2H', 'image')
        h2s = cv2.getTrackbarPos('High2S', 'image')
        h2v = cv2.getTrackbarPos('High2V', 'image')


        # filter red
        mask1 = cv2.inRange(hsv, numpy.array([0, 25, 124]), numpy.array([23, 200, 115]))
        mask2 = cv2.inRange(hsv, numpy.array([154, 198, 30]), numpy.array([178, 239, 241]))

        mask = mask1 | mask2
        res = cv2.bitwise_and(screenshot, screenshot, mask=mask)

        # find contours
        imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, 10, 255, 0)
        im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # draw
        img = screenshot.copy()
        for contour in contours:
            hull = cv2.convexHull(contour)
            cv2.drawContours(img, hull, -1, (0, 255, 0), 3)

        #resized = cv2.resize(img, (1000, 300))
        cv2.imshow('image', img)

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
