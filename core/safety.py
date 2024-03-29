import random

from playwright.sync_api import ElementHandle

from core.fipsitespider import FipSiteSpider


class SafetyTools:
    @classmethod
    def click_to_verify(cls, site: FipSiteSpider, element: ElementHandle):
        box = element.bounding_box()
        uniform = random.uniform(2, 10)
        pos = (box['x'] + box['width'] / 2 + uniform, box['y'] + box['height'] / 2 + uniform)
        site.page.mouse.click(*pos)

    @classmethod
    def slide_to_verify(cls, site: FipSiteSpider, element: ElementHandle, steps=8):
        box = element.bounding_box()
        site.page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        site.page.mouse.down()

        for step in range(1, steps + 1):
            progress = step / steps
            mov_x = box['x'] + box['width'] / 2 + 300 * progress + random.uniform(-5, 5)
            mov_y = box['y'] + box['height'] / 2 + random.uniform(-5, 5)
            site.page.mouse.move(mov_x, mov_y)
            site.wait_for_timeout(random.uniform(0.02, 0.1))

        site.page.mouse.up()
