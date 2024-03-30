import random
from typing import Callable

import ddddocr
import requests
from playwright.sync_api import ElementHandle

from core.fipsitespider import FipSiteSpider


class SafetyTools:

    @classmethod
    def mouse_down_box(cls, site, element):
        box = element.bounding_box()
        site.page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        site.page.mouse.down()
        return box

    @classmethod
    def click_to_verify(cls, site: FipSiteSpider, element: ElementHandle):
        box = element.bounding_box()
        uniform = random.uniform(2, 10)
        pos = (box['x'] + box['width'] / 2 + uniform, box['y'] + box['height'] / 2 + uniform)
        site.page.mouse.click(*pos)

    @classmethod
    def slide_to_verify(cls, site: FipSiteSpider, element: ElementHandle, steps=8):
        box = cls.mouse_down_box(site, element)

        for step in range(1, steps + 1):
            progress = step / steps
            mov_x = box['x'] + box['width'] / 2 + 300 * progress + random.uniform(-5, 5)
            mov_y = box['y'] + box['height'] / 2 + random.uniform(-5, 30)
            site.page.mouse.move(mov_x, mov_y)
            site.wait_for_timeout(random.uniform(0.02, 0.1))

        site.page.mouse.up()

    @classmethod
    def slider_image_to_verify(
            cls,
            site: FipSiteSpider,
            element: ElementHandle,
            background_src,
            target_src,
            steps=8
    ):
        def _get_content():
            for i, url in enumerate([background_src, target_src], start=1):
                img_content = requests.get(url).content
                data.append(img_content)

        det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
        data = []
        _get_content()

        res = det.slide_match(*data, simple_target=True)
        print("==>> res: ", res)
        box = cls.mouse_down_box(site, element)
        print("==>> box: ", box)
        for step in range(1, steps + 1):
            progress = step / steps
            mov_x = box['x'] + box['width'] / 2 + res["target"][0] + random.uniform(5, 10)
            mov_y = box['y'] + box['height'] / 2 + random.uniform(-5, 30)
            site.page.mouse.move(mov_x, mov_y)
            site.wait_for_timeout(random.uniform(0.02, 0.1))

        site.page.mouse.up()
