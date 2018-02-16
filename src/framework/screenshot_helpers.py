from pyautogui import screenshotUtil
from PIL import Image


class Screenshot(object):

    def get_pixel(self, x: int, y: int) -> (float, float, float):
        return screenshotUtil.pixel(x, y)

    def capture(self) -> Image:
        return screenshotUtil.screenshot()

    def matches_color(self, x: int, y: int, color: (float, float, float)) -> bool:
        return screenshotUtil.pixelMatchesColor(x, y, color)
