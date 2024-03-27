from dataclasses import dataclass

from core.fipsitespider import FipSiteSpider
from core.utils import print_log
from sites.hot.model import insert


@dataclass
class Settings:
    platform: str = "掘金"


class JuejinSite(FipSiteSpider):

    def __init__(self):
        super().__init__(connect_over_cdp="http://localhost:9999")
        self.index_url = "https://juejin.cn/hot/articles"
        self.settings = Settings()

    def close(self):
        pass

    @print_log("主任务结束运行")
    def run(self):
        # 1、初始化浏览器
        self.init_site(devtools=False, headless=True)
        self._ctx.set_default_timeout(5000)
        # 2、打开目标网站地址
        self.open(self.index_url)
        self.wait_for_timeout(3)
        self.foreach_hot_list()

    def cleanup(self):
        pass

    @print_log("已入库")
    def parse(self, element):
        link = element.get_attribute("href")
        node = element.query_selector("//div[@class='article-title']")
        title = node.get_attribute("title")
        data = {
            "platform": self.settings.platform,
            "title": title,
            "link": f"https://juejin.cn{link}",
        }
        insert(data)

    @print_log("掘金爬取任务结束")
    def foreach_hot_list(self):
        hot_list_elements = self.find_elements("//a[@class='article-item-link']")
        for el in hot_list_elements:
            self.parse(el)
