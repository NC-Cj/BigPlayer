import json

from loguru import logger
from playwright.sync_api import Locator, Page

from core.fipsitespider import FipSiteSpider

msg = "尊敬的{}HR，我钟意贵公司发布的{}岗位，各方面技术栈都符合，希望能和你取得联系❤️"


class BossSite(FipSiteSpider):
    search_key = "销售"
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
        self.index_url = "https://www.zhipin.com/?ka=header-home"
        self.msg = f"""
尊敬{{company_name}}公司{{hr}}您好：
我是廖先生，正在使用我研发的RPA爬虫框架向您打招呼。
我是一个富有创造力和想法的技术人员，专注于DevOps、后端开发和产品设计。我非常欣赏贵公司的发展和成就，希望能够加入贵公司成为一名员工或者合作伙伴。
我在技术钻研和产品设计领域拥有丰富的经验和专业知识。我对技术创新充满热情，并且善于解决问题和提供创造性解决方案。
如果可能的话，我希望能有机会与贵公司进行面试，详细讨论我如何为贵公司的发展做出贡献。我非常乐意与您分享更多关于我的技能和经验，以及我对技术创新的热情。
我目前处于在职寻找机会的状态，可以随时安排面试。期待能够得到贵公司的回复，共同探讨未来的合作机会。
如需了解更多关于我的项目和经历，请联系我以获取我的简历。
谢谢您的时间和考虑，诚挚期待您的回复！❤

共招呼{{count}}条信息
"""
        self.exclude_list = [
            "中软国际",
            "华为",
            "MOSYNX"
        ]

    def check_company(self, name):
        return name in self.exclude_list

    @staticmethod
    def insert(data):
        db.session.add(data)
        db.session.commit()
        db.session.close()

    @staticmethod
    def check_exist(company_name):
        return bool(db.session.query(db.Boss).filter_by(company_name=company_name).first())

    @staticmethod
    def get_total():
        return db.session.query(db.Boss).count()

    @staticmethod
    def _format(data, mod):
        if mod == 1:
            return data.split(" ")[0]
        else:
            raise NotImplemented

    def goto_index_page(self):
        self.open(self.setting["url"])
        logger.debug("主页打开成功")

    def search_job(self):
        self.fill_element("//input[@class='ipt-search']", self.search_key)
        self.click_element("//button[@class='btn btn-search']")
        logger.debug("岗位关键字搜索成功")

    def next_page(self):
        self.click_element("(//div[@class='options-pages']//a/i)[2]")

    def city_element(self):
        return self.find_element("//*/ul[@class='dropdown-city-list']")

    def get_city_code(self, city_name):
        with open("./lib/cityCode.json", "r", encoding='utf-8') as f:
            data = json.load(f)

        return data[city_name]

    def run(self):
        self.init_site(headless=False)
        self.open(self.index_url)
        if isinstance(self.city, str):
            url = f"{self.page.url.split('city=')[0]}city={self.get_city_code(self.city)}"
            self.open(url)

        self.search_job()

        self.wait_for_element("//ul[@class='job-list-box']")
        job_list_elements = self.find_elements("//*/li[@class='job-card-wrapper']")
        for el in job_list_elements:
            # try:
            self.click_open_new_page(el)
            self.switch_page()

            hr = self.wait_for_element("//h2[@class='name']").text_content()
            self._format(hr, 1)
            company_name = self.find_element("//li[@class='company-name']/span", True).text_content()
            job_title = self.find_element("//span[@class='job-title']").text_content()
            print(hr)
            print(company_name)
            print(job_title)
            # self.page: Page
            self.page.pause()

            # TODO: 判断公司是否沟通过
            if self.page.get_by_role("link", name="投递简历"):
                self.close_current_page()
            else:
                self.page.get_by_role("link", name="立即沟通").click()
                chat = self.page.get_by_placeholder("请简短描述您的问题")
                message = msg.format(hr, job_title)
                chat.fill(message)
                self.press_key("Enter")

            self.switch_page()
            self.wait_for_timeout(3)


# self.goto_index_page()
# count = 0

# for key in self.setting["job_title"]:
#     self.search(key)
#     self.wait_for_timeout(5)

#     for _ in range(self.setting["on_task_page"]):
#         self.wait_for_timeout(3)
#         # job_list_elements = self.find_elements("//li[@class='job-card-wrapper']")
#         for i in range(1, 31):
#             el = self.find_element(
#                 f"(//li[@class='job-card-wrapper'])[{i}]")
#             company_name = self.element_query(
#                 el, "//h3/a").text_content()
#             job_name = self.element_query(
#                 el, "//span[@class='job-name']").text_content()
#             salary = self.element_query(
#                 el, "//span[@class='salary']").text_content()
#             hrname = self.element_query(
#                 el, "//div[@class='info-public']").text_content()
#             hrposition = self.element_query(
#                 el, "//div[@class='info-public']/em").text_content()
#             address = self.element_query(
#                 el, "//span[@class='job-area']").text_content()
#             hr = hrname
#             # print(company_name, job_name, salary, address, hr)
#             print(
#                 f"{company_name:10s}{job_name:10s}{salary:12s}{address:10s}{hr:10s}")

#             if self.check_exist(company_name) is True:
#                 continue

#             self.insert(db.Boss(company_name=company_name,
#                                 job_name=job_name,
#                                 salary=salary,
#                                 address=address,
#                                 category=key))

#             self.click_element(f"(//div[@class='info-public'])[{i}]")
#             self.wait_for_timeout(3)
#             # self.click_element("//div[@contenteditable='true']")
#             count += 1
#             row += 1
#             self.fill_element(
#                 "//div[@contenteditable='true']",
#                 self.msg.format_map({
#                     "company_name": company_name,
#                     "hr": hr,
#                     "count": row
#                 })
#             )
#             self.press_key("Enter")
#             self.wait_for_timeout(1)
#             self.go_back()
#             self.wait_for_timeout(3)

#         self.next_page()

def get_all_current_companies(self):
    return self.find_elements("//*[@class='company-name']/a")
