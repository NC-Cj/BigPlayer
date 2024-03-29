from loguru import logger

from core.fipsitespider import FipSiteSpider
from core.safety import SafetyTools
from sites.hot.model import setup


class D(FipSiteSpider):

    def __init__(self):
        super().__init__(connect_over_cdp="http://localhost:9999")
        self.index_url = "https://dun.163.com/trial/sense"

    def run(self):
        # 1、初始化数据库
        setup()
        # 2、初始化浏览器
        self.init_site(devtools=False, headless=True)
        self._ctx.set_default_timeout(15000)
        # 3、打开目标网站地址
        self.open(self.index_url)
        self.wait_for_timeout(3)
        self.for_job()

        self.page.pause()

    def for_job(self):
        test_work = [
            self.test_click_to_verify,
            self.test_slide_to_verify,
        ]
        for i in range(10):
            if i > 1:
                break
            self.click_element(f"//dl[@class='m-tnavigator__item'][1]/dd[{i + 1}]/a")
            logger.debug("start job")
            test_work[i]()
            self.wait_for_timeout(3)
        logger.debug("All jobs are done")
        self.wait_for_timeout(100)

    def test_click_to_verify(self):

        if e := self.find_element("//div[@class='yidun_intelli-tips']"):
            SafetyTools.click_to_verify(self, e)
            logger.debug("Click to verify is successful")
        else:
            logger.warning("Click to verify is failed")

    def test_slide_to_verify(self):
        if e := self.find_element("//span[@class='yidun_slider__icon']"):
            SafetyTools.slide_to_verify(self, e)
            logger.debug("Slide to verify is successful")
        else:
            logger.warning("Slide to verify is failed")


if __name__ == '__main__':
    with D() as site:
        site.run()
