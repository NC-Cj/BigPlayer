import re
from dataclasses import dataclass

from core.fipsitespider import FipSiteSpider
from core.utils import print_log
from sites.applyJob.boss.asset.message import *

msg = msg_developer

count = 0


def _extract_salary_range(salary_str):
    if match := re.match(r'(\d+)-(\d+)K', salary_str):
        salary_min, salary_max = map(int, match.groups())
    elif match := re.match(r'(\d+)K', salary_str):
        salary_min, salary_max = int(match[1]), int(match[1])
    else:
        return None, None

    return salary_min * 1000, salary_max * 1000


@dataclass
class Settings:
    category: str = "技术支持python"
    expect_city: str = "苏州"
    min_expect_salary: int = 8000  # 最小期望薪资
    max_expect_salary: int = 20000  # 最大期望薪资
    median_expect_salary: int = 10000  # 期望额度，特定情况下主动调整岗位薪资最小、最大带来的差距
    exclude_list: tuple = ("中软国际", "软通动力", "华为", "上海微创软件", "博彦科技")  # 这是已知的外包公司，请自行修改
    crawling_page_number: int = 1


class ZhilinSite(FipSiteSpider):

    def __init__(self):
        super().__init__(connect_over_cdp="http://localhost:9999")
        self.index_url = "https://www.zhaopin.com/"
        self.settings = Settings()

    @print_log("主任务结束运行")
    def run(self):
        self.init_site(devtools=False, headless=True)
        self._ctx.set_default_timeout(5000)
        self.open(self.index_url)

        self.search_job()
        while self.settings.crawling_page_number >= 1:
            self.wait_for_timeout(3)
            self.foreach_job_list()
            # self.next_page()
            self.settings.crawling_page_number -= 1

    @print_log("返回职位列表")
    def cleanup(self):
        self.page.close()
        self.switch_page()

    @print_log("工作数据处理完成，开始下一个工作求职")
    def parse(self, element):
        self.click_element_and_switch_page(element.query_selector("//button[@type='button']"))

    def search_job(self):
        self.fill_element("//input[@placeholder='搜索职位、公司']", self.settings.category)
        self.click_element_and_switch_page("//button[@class='search-wrapper__button']")

    def foreach_job_list(self):
        job_list_elements = self.find_elements("//div[@class='joblist-box__item clearfix']")
        for el in job_list_elements:
            self.parse(el)
            self.cleanup()
