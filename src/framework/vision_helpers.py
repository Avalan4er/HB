import cv2
import numpy
from PIL import Image

import framework_objects
from logger import logger


def is_color_in_range(color, range_center, range_width=3) -> bool:
    for delta_color_component in numpy.subtract(color, range_center):
        if abs(
                delta_color_component) > range_width:  # проверка если цвета пикселя и эталона различаются больше чем на 3
            return False  # то такой контур нам не подходит

    return True

def get_health(screenshot: Image) -> float:
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
        if 17 < h < 40:
            return (w / 208) * 100

    return 0


def detect_units(screenshot: Image):
    screenshot = cv2.cvtColor(
        numpy.array(screenshot),
        cv2.COLOR_RGB2BGR)

    image = screenshot.copy()

    #  закрашиваем некоторые части экрана которые создают кучу неправильных контуров
    cv2.rectangle(image, (1490, 750), (1920, 1080), (255, 255, 255), -1)  # закрашиваем миникарту
    cv2.rectangle(image, (360, 0), (1546, 120), (255, 255, 255), -1)  # закрашиваем панель героев

    image = cv2.bitwise_not(image)

    # filter health bar color
    mask_enemy_hero_health = cv2.inRange(image, numpy.array([206, 220, 219]), numpy.array([208, 222, 221]))
    mask_enemy_creep_health = cv2.inRange(image, numpy.array([255, 255, 255]), numpy.array([255, 255, 255]))
    mask = mask_enemy_creep_health | mask_enemy_hero_health  # build mask
    res = cv2.bitwise_and(image, image, mask=mask)  # apply mask

    # find contours
    image_grayscale = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)  # convert filtered img to greyscale
    _, image_bw = cv2.threshold(image_grayscale, 1, 255, cv2.THRESH_BINARY)  # then convert to black/white
    _, contours, hierarchy = cv2.findContours(image_bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # find contours

    enemy_creep_plate_color = numpy.array([55, 0, 187])     # цвет индикатора здоровья врага
    result = []
    for contour in contours:
        if cv2.contourArea(contour) < 30:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        unit = framework_objects.Unit(framework_objects.Point(x + (w / 2), y))

        if is_color_in_range(screenshot[y + 1, x + 1], enemy_creep_plate_color):
            unit.is_enemy = True

        if w in range(53, 55) and h in range(5, 7):  # creep
            unit.type = framework_objects.CreepUnitType()

        elif w in range(146, 150) and h in range(10, 12):  # fort
            unit.type = framework_objects.TowerUnitType()

        elif w in range(123, 125) and h in range(11, 13):  # hero
            unit.type = framework_objects.HeroUnitType()

        elif w in range(134, 136) and h in range(6, 8):  # gates
            unit.type = framework_objects.GatesUnitType()

        else:  # кто то не понятный и явно не подходящий для атаки
            continue

        if unit not in result:
            result.append(unit)
            # cv2.drawContours(screenshot, [contour], -1, (0, 255, 0), 1)

    # cv2.namedWindow('img')
    # cv2.imshow('img', screenshot)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return result


def map_get_player_coords(screenshot: Image):
    screenshot = cv2.cvtColor(
        numpy.array(screenshot),
        cv2.COLOR_RGB2BGR)

    image = screenshot.copy()

    #  закрашиваем все кроме миникарты
    cv2.rectangle(image, (0, 0), (1920, 720), (0, 0, 0), -1)
    cv2.rectangle(image, (0, 720), (1490, 1080), (0, 0, 0), -1)

    # filter health bar color
    mask_enemy_hero_health = cv2.inRange(image, numpy.array([0, 100, 30]), numpy.array([60, 255, 100]))
    mask = mask_enemy_hero_health  # build mask
    res = cv2.bitwise_and(image, image, mask=mask)  # apply mask

    # find contours
    image_grayscale = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)  # convert filtered img to greyscale
    _, image_bw = cv2.threshold(image_grayscale, 1, 255, cv2.THRESH_BINARY)  # then convert to black/white
    _, contours, hierarchy = cv2.findContours(image_bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # find contours

    for contour in contours:
        area = cv2.contourArea(contour)
        if 300 < area < 320:
            x, y, w, h = cv2.boundingRect(contour)
            return framework_objects.Point(x + (w / 2), y + (h / 2))

    return None


def screenshot_find_templates(screenshot: Image, template_path: str):
    image = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2GRAY)
    if image is None:
        logger.error('Что то пошло катастрофически не так. Изображения в котором ищется шаблон не создалось')

    template = cv2.imread(template_path, 0)
    if template is None:
        logger.error('Ошбика чтения файла шаблона ' + template_path)

    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    ts = 0.9
    loc = numpy.where(res >= ts)

    result = []
    for pt in zip(*loc[::-1]):
        point = framework_objects.Point(pt[0], pt[1])
        if point not in result:
            result.append(point)

    return result


def screenshot_contains_template(screenshot: Image, template_path: str) -> bool:
    template_coordinates = screenshot_find_templates(screenshot, template_path)
    if len(template_coordinates) > 0:
        return True

    return False
