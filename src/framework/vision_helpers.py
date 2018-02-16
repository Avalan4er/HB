import cv2
import numpy
import logging
from PIL import Image


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
        if 17 < h < 23:
            return (w / 208) * 100

    return 0


def find_all_enemy_creeps(screenshot: Image) -> (int, int):
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
    ret, thresh = cv2.threshold(image_grayscale, 1, 255, cv2.THRESH_BINARY)  # then convert to black/white
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # find contours

    enemy_creep_plate_color = numpy.array([55, 0, 187])     # цвет индикатора здоровья врага
    result = []
    for contour in contours:
        if cv2.contourArea(contour) < 30:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        if ((w in range(53,55) and h in range(5,7)) or          # creep
            (w in range(146, 150) and h in range(10, 12)) or    # fort
            (w in range(123, 125) and h in range(11, 13)) or    # hero
            (w in range(134, 136) and h in range(6, 8))):       # gates

            # если цвет плашки крипа вражеский
            for delta_color_component in numpy.subtract(screenshot[y + 1, x + 1], enemy_creep_plate_color):
                if abs(delta_color_component) > 3: # проверка если цвета пикселя и эталона различаются больше чем на 3
                    break   # то такой контур нам не подходит

                if (x, y) not in result:
                    result.append((x + (w /2), y))
                    # cv2.drawContours(screenshot, [contour], -1, (0, 255, 0), 1)

    # cv2.namedWindow('img')
    # cv2.imshow('img', screenshot)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return result


def screenshot_get_template_coords(screenshot: Image, template_path: str) -> (int, int):
    image = cv2.cvtColor(numpy.array(screenshot), cv2.COLOR_RGB2GRAY)
    if image is None:
        logging.error('Что то пошло катастрофически не так. Изображения в котором ищется шаблон не создалось')

    template = cv2.imread(template_path, 0)
    if template is None:
        logging.error('Ошбика чтения файла шаблона ' + template_path)

    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    ts = 0.9
    loc = numpy.where(res >= ts)

    for pt in zip(*loc[::-1]):
        return pt


def screenshot_contains_template(screenshot: Image, template_path: str) -> bool:
    point = screenshot_get_template_coords(screenshot, template_path)
    if point is not None:
        return True

    return False
