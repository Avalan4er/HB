import cv2
import numpy


def find_closest_enemy_creep(screenshot):
    screenshot = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2BGR)

    # filter health bar color
    mask_enemy_health = cv2.inRange(screenshot, numpy.array([55, 0, 187]), numpy.array([63, 0, 215]))
    mask = mask_enemy_health  # build mask
    res = cv2.bitwise_and(screenshot, screenshot, mask=mask)  # apply mask

    # find contours
    imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)  # convert filtered img to greyscale
    ret, thresh = cv2.threshold(imgray, 1, 255, cv2.THRESH_BINARY)  # then convert to black/white
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # find contours

    for contour in contours:
        area = cv2.contourArea(contour)
        if 10 < area < 100:
            x, y, w, h = cv2.boundingRect(contour)
            return x, y

    return None
