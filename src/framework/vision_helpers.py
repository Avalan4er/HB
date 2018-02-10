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


def screenshot_contains_template(screenshot, template_path):
    width, height = screenshot.size
    image = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2GRAY)[0:300, 0:width]
    template = cv2.imread(template_path, 0)

    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    ts = 0.9
    loc = numpy.where(res >= ts)

    for pt in zip(*loc[::-1]):
        return True
