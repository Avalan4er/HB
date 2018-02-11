import cv2
import numpy


def get_health(screenshot):
    screenshot = cv2.cvtColor(
        numpy.array(screenshot),
        cv2.COLOR_RGB2BGR)
    mask_healthbar = cv2.inRange(screenshot, numpy.array([19, 149, 55]), numpy.array([100, 240, 171]))
    mask = mask_healthbar  # build mask
    res = cv2.bitwise_and(screenshot, screenshot, mask=mask)  # apply mask

    imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)  # convert filtered img to greyscale
    ret, thresh = cv2.threshold(imgray, 1, 255, cv2.THRESH_BINARY)  # then convert to black/white
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # find contours

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if 17 < h < 23:
            return (w / 208) * 100

    return 0


def find_all_enemy_creeps(screenshot):
    screenshot = cv2.cvtColor(
        numpy.array(screenshot),
        cv2.COLOR_RGB2BGR)

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
        if 40 < area < 200:
            x, y, w, h = cv2.boundingRect(contour)
            if 3 < h < 6:
                yield x, y #x + 300, y + 100

    return None


def screenshot_contains_template(screenshot, template_path):
    image = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2GRAY)
    template = cv2.imread(template_path, 0)

    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    ts = 0.9
    loc = numpy.where(res >= ts)

    for pt in zip(*loc[::-1]):
        return True
