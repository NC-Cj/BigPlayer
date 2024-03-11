import contextlib
import json
import os
import re
import traceback

from loguru import logger

from core.fipsitespider import FipSiteSpider
from core.utils import print_log
from .db import setup, Boss, insert

msg = "尊敬的{hr}HR，我钟意贵公司发布的{job}岗位，各方面技术栈都符合，希望能和你取得联系❤️\n\n" \
      "目前状态：在职，寻找机会中\n" \
      "最快到岗时间：按规定一般在提交离职申请一个月以内\n" \
      "面试接受度：当前工作地点：{address}，{interview}\n" \
      "期望薪资：当前职位薪资范围符合\n" \
      "是否对项目有过0-1的经验：有过数十个项目0-1孵化经历\n" \
      "个人简介：学习能力强，善于表达，汇报、交流能力好，能够快速融入团队，理解并习惯scrum工作方式，对产品从调研、设计、研发有过完整经验，有pm能力\n\n" \
      "招聘助手正在向你发送信息，开源地址：https://github.com/NC-Cj/BigPlayer"


def _get_city_code(city_name):
    path = os.path.join(os.getcwd(), "asset", "cityCode.json")
    with open(path, "r", encoding='utf-8') as f:
        data = json.load(f)

    return data.get(city_name)


def _extract_salary_range(salary_str):
    if match := re.match(r'(\d+)-(\d+)K', salary_str):
        salary_min, salary_max = map(int, match.groups())
    elif match := re.match(r'(\d+)K', salary_str):
        salary_min, salary_max = int(match[1]), int(match[1])
    else:
        return None, None

    return salary_min * 1000, salary_max * 1000


def _check_exclude(c, exclude_list):
    return any(exclude_item in c for exclude_item in exclude_list)


class BossSite(FipSiteSpider):
    category = "python开发"
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
        self.exclude_list = []
        self.now_city = "苏州"
        self.page_number = 2
        self.max_expect_value = 12000
        self.min_expect_value = 16000

    @print_log("主任务结束运行")
    def run(self):
        self.init_site(devtools=False, headless=True)
        self._ctx.set_default_timeout(5000)
        self.open(self.index_url)

        self.search_job()
        self.choice_city()

        while self.page_number >= 1:
            self.wait_for_timeout(3)
            self.foreach_job_list()
            self.next_page()
            self.page_number -= 1

    def next_page(self):
        p = int(self.page.url[-1])
        url = self.page.url[:-1] + (str(p + 1))
        self.open(url)

    @print_log("返回职位列表")
    def cleanup(self):
        self.close_current_page()
        self.switch_page()
        self.wait_for_timeout(2)

    @print_log("工作数据处理完成，开始下一个工作求职")
    def parse(self):
        if match := re.search(r"/job_detail/(.*?).html", self.page.url):
            job_id = match[1]
        else:
            return

        if self.query_company(job_id):
            return

        hr = self.get_element_text("//h2[@class='name']")
        company_name = self.get_element_text("//li[@class='company-name']", True)
        salary = self.get_element_text("//span[@class='salary']")
        job_title = self.get_element_text("//div[@class='name']/h1")
        address = self.get_element_text("//div[@class='location-address']")

        if not address:
            return

        if not company_name:
            company_name = "Unknown"

        hr = hr.split(" ")[0].strip()
        company_name = company_name.lstrip("公司名称")
        address = address.strip()
        salary = salary.strip()
        min_salary, max_salary = _extract_salary_range(salary)

        if _check_exclude(company_name, self.exclude_list):
            return

        with contextlib.suppress(Exception):
            if self.go_chat_boss(hr, job_title, address):
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

    def _close(self):
        logger.warning("进程被主动结束")
        super().close()
        os._exit(0)

    @print_log("搜索岗位成功")
    def search_job(self):
        self.fill_element("//input[@class='ipt-search']", self.category)
        self.click_element("//button[@class='btn btn-search']")

    @print_log("正在重新选择城市")
    def choice_city(self):
        if city_code := _get_city_code(self.city):
            if self.page.url.split("=")[-1] != city_code and isinstance(self.city, str):
                url = f"{self.page.url.split('city=')[0]}city={city_code}&page=1"
                self.open(url)
        else:
            raise KeyError("Invalid city")

    @print_log("当前页面处理完成")
    def foreach_job_list(self):
        self.wait_for_element("//ul[@class='job-list-box']")
        job_list_elements = self.find_elements("//li[@class='job-card-wrapper']")
        for el in job_list_elements:
            if self.read_salary(el):
                continue

            try:
                if self.goto_job_details(el) is False:
                    self.parse()
            except Exception:
                traceback.print_exc()
            finally:
                self.cleanup()

    @print_log("发布求职信息成功")
    def go_chat_boss(self, hr, job_title, address):
        def chat_again():
            self.page.locator("span").filter(has_text="继续沟通").click()

            if self.has_dialog():
                self.page.pause()

            interview = f"是否可以远程面试，合适再进行现场面试（我目前所在地{self.now_city}）" if self.now_city not in address else "可以现场面试"
            message = msg.format(hr=hr, job=job_title, address=address, interview=interview)
            self.fill_element("//div[@class='chat-input']", message)
            self.wait_for_timeout(2)  # 过快发送信息会导致异常
            self.press_key("Enter")
            return True

        self.page.get_by_role("link", name="立即沟通").click()

        if self.if_been_maximum():
            self._close()

        if self.has_dialog():
            if self.if_chat_ok():
                return chat_again()
            else:
                # 如果弹窗不是招呼成功，可能来自学历不匹配或其它"要求性"告知弹窗
                pass

            return True
        else:
            return chat_again()

    @print_log("正在进入职位详情页")
    def goto_job_details(self, el):
        self.click_element_and_switch_page(el)
        return self.has_dialog()

    @print_log("查询该公司是否已投递简历")
    def query_company(self, path):
        return self.db.query(Boss.id).filter_by(path=path).count()

    def has_dialog(self):
        return bool(self.find_element("//div[@class='dialog-container']", nullable=True, timeout=2 * 1000))

    def if_chat_ok(self):
        return bool(self.page.get_by_text("已向BOSS发送消息", exact=True))

    def if_been_maximum(self):
        return bool(self.find_element("//p[contains(text(), '请明天再试')]", nullable=True, timeout=2 * 1000))

    def read_salary(self, element):
        try:
            if salary_el := element.query_selector("//span[@class='salary']"):
                salary_min, salary_max = _extract_salary_range(salary_el.text_content())
                if salary_min > self.min_expect_value:
                    return True
                if self.max_expect_value - salary_max > 2000:
                    return True
            return False
        except Exception as e:
            traceback.print_exc()
            return True
