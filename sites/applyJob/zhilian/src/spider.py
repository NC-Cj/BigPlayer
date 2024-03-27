from dataclasses import dataclass

from core.fipsitespider import FipSiteSpider
from core.utils import print_log


@dataclass
class Settings:
    category: str = "python工程"


class ZhilinSite(FipSiteSpider):

    def __init__(self):
        super().__init__(connect_over_cdp="http://localhost:9999")
        self.index_url = "https://www.zhaopin.com/"
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
        # 3、搜索关键字进入岗位列表
        self.search_job()
        self.wait_for_timeout(3)
        # 4、循环点击每个岗位进入详情页
        self.switch_page()
        self.foreach_job_list()
        self.close()

    @print_log("返回职位列表")
    def cleanup(self):
        self.page.close()
        self.switch_page()

    @print_log("工作数据处理完成，开始下一个工作求职")
    def parse(self):
        pass

    def search_job(self):
        self.fill_element("//input[@placeholder='搜索职位、公司']", self.settings.category)
        self.click_element("//button[@class='search-wrapper__button']")

    def foreach_job_list(self):
        job_list_elements = self.find_elements("//div[@class='joblist-box__item clearfix']")
        for el in job_list_elements:
            self.click_element_and_switch_page(el)
            self.wait_for_timeout(2)
            # 关闭详情页继续下一个任务
            self.cleanup()
