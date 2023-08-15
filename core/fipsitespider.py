from core.basespider import BaseSpider
from db import db


class FipSiteManager:
    pass


class BossSite(BaseSpider):

    def __init__(self):
        super().__init__(connect_over_cdp="http://localhost:9999", headless=False)
        self.setting = {
            "url": "https://www.zhipin.com/suzhou/",
            "job_title": ["python"],
            "on_task_page": 5
        }
        self.msg = f"""
尊敬{{company_name}}公司{{hr}}您好：
我是廖先生，一个富有创造力和想法的技术人员，专注于DevOps、后端开发和产品设计。我非常欣赏贵公司的发展和成就，希望能够加入贵公司成为一名员工或者合作伙伴。
我在DevOps工具开发、后端开发和产品设计领域拥有丰富的经验和深厚的专业知识。我对技术创新充满热情，并且善于解决问题和提供创造性解决方案。
目前，我正积极寻找新的职业发展机会，对贵公司的工作机会非常感兴趣。我是一位快速学习和适应新环境的人，具备良好的团队合作能力和沟通能力。我相信我的技术和创造力将为贵公司带来巨大的价值。
如果可能的话，我希望能有机会与贵公司进行面试，详细讨论我如何为贵公司的发展做出贡献。我非常乐意与您分享更多关于我的技能和经验，以及我对技术创新的热情。
我目前处于在职寻找机会的状态，可以随时安排面试。期待能够得到贵公司的回复，共同探讨未来的合作机会。
如需了解更多关于我的项目和经历，请联系我以获取我的简历。
谢谢您的时间和考虑，诚挚期待您的回复！❤

今日已招呼{{count}}条信息
"""

    @staticmethod
    def insert(data):
        db.session.add(data)
        db.session.commit()
        db.session.close()

    @staticmethod
    def check_exist(company_name):
        return bool(db.session.query(db.Boss).filter_by(company_name=company_name).first())

    def goto_index_page(self):
        self.open(self.setting["url"])

    def search(self, key):
        self.fill_element("//input[@class='ipt-search']", key)
        self.click_element("//button[@class='btn btn-search']")

    def next_page(self):
        self.click_element("(//div[@class='options-pages']//a/i)[2]")

    def run(self):
        self.goto_index_page()
        count = 0
        row = 0

        for key in self.setting["job_title"]:
            self.search(key)
            self.wait_for_timeout(5)

            for _ in range(self.setting["on_task_page"]):
                self.wait_for_timeout(3)
                job_list_elements = self.find_elements("//li[@class='job-card-wrapper']")
                for i in range(1, len(job_list_elements) + 1):
                    el = self.find_element(f"(//li[@class='job-card-wrapper'])[{i}]")
                    company_name = self.element_query(el, "//h3/a").text_content()
                    job_name = self.element_query(el, "//span[@class='job-name']").text_content()
                    salary = self.element_query(el, "//span[@class='salary']").text_content()
                    hrname = self.element_query(el, "//div[@class='info-public']").text_content()
                    hrposition = self.element_query(el, "//div[@class='info-public']/em").text_content()
                    address = self.element_query(el, "//span[@class='job-area']").text_content()
                    hr = hrname
                    row += 1
                    # print(company_name, job_name, salary, address, hr)
                    print(f"{company_name:10s}{job_name:10s}{salary:12s}{address:10s}{hr:10s}")

                    if self.check_exist(company_name) is True:
                        continue

                    self.insert(db.Boss(company_name=company_name,
                                        job_name=job_name,
                                        salary=salary,
                                        address=address,
                                        category=key))

                    self.click_element(f"(//div[@class='info-public'])[{row}]")
                    self.wait_for_timeout(3)
                    # self.click_element("//div[@contenteditable='true']")
                    count += 1

                    self.fill_element(
                        "//div[@contenteditable='true']",
                        self.msg.format_map({
                            "company_name": company_name,
                            "hr": hr,
                            "count": count
                        })
                    )
                    self.press_key("Enter")
                    self.wait_for_timeout(1)
                    self.go_back()
                    self.wait_for_timeout(3)

                self.next_page()
                row = 0
