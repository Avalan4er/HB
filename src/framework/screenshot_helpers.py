from pyautogui import screenshotUtil

class screenshot(object):

    def get_pixel(self, x, y):
        return screenshotUtil.pixel(x,y)

    def capture(self):
        return screenshotUtil.screenshot()

    def matches_color(self, x, y, color):
        return screenshotUtil.pixelMatchesColor(x, y, color)


