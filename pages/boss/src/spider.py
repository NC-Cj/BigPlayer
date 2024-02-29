import json
import os
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


def _format(data, mod):
    if mod == 1:
        return data.split(" ")[0]
    else:
        raise NotImplemented


class BossSite(FipSiteSpider):
    search_key = "汽车零件"
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
        if isinstance(self.city, str):
            url = f"{self.page.url.split('city=')[0]}city={_get_city_code(self.city)}"
            self.open(url)

        self.search_job()
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

        hr = hr.split(" ")[0]
        company_name = company_name.strip("公司名称")
        salary = salary.strip("公司名称")

        job_title = self.get_element_text("//span[@class='job-title']")
        address = self.get_element_text("//div[@class='location-address']")

        if not company_name:
            company_name = "Unknown"
        if company_name in self.exclude_list:
            self.close_current_page()

        if self.query_company(company_name, self.page.url):
            self.close_current_page()
        elif self.go_chat_boss(hr, job_title):
            data = {
                "company": company_name,
                "job_title": job_title,
                "salary": salary,
                "address": address,
                "category": self.search_key,
                "link": self.page.url
            }
            insert(data)

    @print_log("搜索岗位成功")
    def search_job(self):
        self.fill_element("//input[@class='ipt-search']", self.search_key)
        self.click_element("//button[@class='btn btn-search']")

    @print_log("当前页面处理完成")
    def foreach_job_list(self):
        self.wait_for_element("//ul[@class='job-list-box']")
        job_list_elements = self.find_elements("//*/li[@class='job-card-wrapper']")
        for el in job_list_elements:
            try:
                self.goto_job_details(el)
                self.parse()
                self.cleanup()
            except Exception:
                traceback.print_exc()

    @print_log("发布求职信息成功")
    def go_chat_boss(self, hr, job_title):
        self.page.get_by_role("link", name="立即沟通", disabled=False).click()
        chat = self.page.get_by_placeholder("请简短描述您的问题")
        message = msg.format(hr, job_title)
        chat.fill(message)
        self.press_key("Enter")
        return True

    @print_log("正在进入职位详情页")
    def goto_job_details(self, el):
        self.click_popup(el)
        self.switch_page()

    @print_log("查询该公司是否已投递简历")
    def query_company(self, company_name, ulr):
        if company_name == "Unknown":
            return self.db.query(Boss).filter_by(link=ulr).first()
        return self.db.query(Boss).filter_by(company=company_name).first()
