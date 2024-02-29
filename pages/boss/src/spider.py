import contextlib
import json
import os
import re
import traceback

from core.fipsitespider import FipSiteSpider
from core.utils import print_log
from .db import setup, Boss, insert

msg = "尊敬的{}HR，我钟意贵公司发布的{}岗位，各方面技术栈都符合，希望能和你取得联系❤️"


@print_log("获取城市代码")
def _get_city_code(city_name):
    path = os.path.join(os.getcwd(), "asset", "cityCode.json")
    with open(path, "r", encoding='utf-8') as f:
        data = json.load(f)

    return data[city_name]


def extract_salary_range(salary_str):
    if match := re.match(r'(\d+)-(\d+)K', salary_str):
        salary_min, salary_max = map(int, match.groups())
    elif match := re.match(r'(\d+)K', salary_str):
        salary_min, salary_max = int(match[1]), int(match[1])
    else:
        return None, None

    return salary_min * 1000, salary_max * 1000


class BossSite(FipSiteSpider):
    category = "服务产品经理"
    # city = [
    #     "苏州",
    #     "南京",
    #     "南昌",
    #     "广东",
    #     "珠海",
    #     "福州",
    #     "厦门",
    #     "杭州"
    # ]
    city = "南昌"
    ul_city = [
        "ABCDE",
        "FGHJ",
        "KLMN",
        "PQRST",
        "WXYZ"
    ]

    def __init__(self):
        super().__init__(connect_over_cdp="http://localhost:9999")
        self.db = setup()
        self.index_url = "https://www.zhipin.com/?ka=header-home"
        self.exclude_list = [
            "中软国际",
            "华为",
            "MOSYNX"
        ]

    @print_log("主任务结束运行")
    def run(self):
        self.init_site(devtools=False, headless=True)
        self.open(self.index_url)
        city_code = _get_city_code(self.city)
        self.search_job()

        if self.page.url.split("=")[-1] != city_code and isinstance(self.city, str):
            url = f"{self.page.url.split('city=')[0]}city={city_code}"
            self.open(url)

        self.wait_for_timeout(3)
        self.foreach_job_list()

    @print_log("返回职位列表")
    def cleanup(self):
        self.close_current_page()
        self.switch_page()
        # self.wait_for_timeout(3)

    @print_log("工作数据处理完成，开始下一个工作求职")
    def parse(self):
        hr = self.wait_for_element("//h2[@class='name']").text_content()
        company_name = self.get_element_text("//li[@class='company-name']", True)
        salary = self.get_element_text("//span[@class='badge']")
        job_title = self.get_element_text("//span[@class='job-title']")
        address = self.get_element_text("//div[@class='location-address']")

        hr = hr.split(" ")[0]
        company_name = company_name.lstrip("公司名称")
        salary = salary.strip("公司名称")
        min_salary, max_salary = extract_salary_range(salary)

        if match := re.search(r"/job_detail/(.*?).html", self.page.url):
            job_id = match[1]
        else:
            return

        if not company_name:
            company_name = "Unknown"
        if company_name in self.exclude_list:
            return

        if self.query_company(job_id):
            return

        with contextlib.suppress(Exception):
            if self.go_chat_boss(hr, job_title):
                data = {
                    "company": company_name,
                    "job_title": job_title,
                    "min_salary": min_salary,
                    "max_salary": max_salary,
                    "address": address,
                    "category": self.category,
                    "path": job_id,
                    "city": self.city,
                }
                insert(data)

    @print_log("搜索岗位成功")
    def search_job(self):
        self.wait_for_element("//input[@class='ipt-search']").fill(self.category)
        self.click_element("//button[@class='btn btn-search']")

    @print_log("当前页面处理完成")
    def foreach_job_list(self):
        self.wait_for_element("//ul[@class='job-list-box']")
        job_list_elements = self.find_elements("//*/li[@class='job-card-wrapper']")
        for el in job_list_elements:
            try:
                if self.goto_job_details(el) is not False:
                    self.parse()
                self.cleanup()
            except Exception:
                traceback.print_exc()

    @print_log("发布求职信息成功")
    def go_chat_boss(self, hr, job_title):
        self.page.get_by_role("link", name="立即沟通").click()
        chat = self.page.get_by_placeholder("请简短描述您的问题")
        message = msg.format(hr, job_title)
        chat.fill(message)
        self.press_key("Enter")
        return True

    @print_log("正在进入职位详情页")
    def goto_job_details(self, el):
        self.click_popup(el)
        self.switch_page()

        if self.wait_for_element("//div[@class='dialog-container']", 2000, True):
            return False

    @print_log("查询该公司是否已投递简历")
    def query_company(self, path):
        return self.db.query(Boss).filter_by(path=path).first()
