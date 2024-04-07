import contextlib
import json
import os
import re
import traceback
from dataclasses import dataclass

from core.fipsitespider import FipSiteSpider
from core.utils import print_log
from sites.applyJob.boss.asset.message import *
from sites.applyJob.model import *

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


class BossSite(FipSiteSpider):

    def __init__(self):
        super().__init__(connect_over_cdp="http://localhost:9999")
        self.platform = "boss"
        self.index_url = "https://www.zhipin.com/?ka=header-home"
        self.now_city = "苏州"
        self.crawling_page_number = 3
        self.settings = Settings()

    @property
    def get_city_code(self):
        path = os.path.join(os.getcwd(), "asset", "cityCode.json")
        with open(path, "r", encoding='utf-8') as f:
            data = json.load(f)

        return data.get(self.settings.expect_city)

    @print_log("主任务结束运行")
    def run(self):
        setup()
        self.init_site(devtools=False, headless=True)
        self._ctx.set_default_timeout(5000)
        self.open(self.index_url)

        self.search_job()
        self.choice_city()

        while self.crawling_page_number >= 1:
            self.wait_for_timeout(3)
            self.foreach_job_list()
            self.next_page()
            self.crawling_page_number -= 1

    @print_log("执行下一页")
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

        if company_exists(job_id):
            return

        address = self.get_element_text("//div[@class='location-address']")
        if not address:
            return

        hr = self.get_element_text("//h2[@class='name']")
        salary = self.get_element_text("//span[@class='salary']")
        job_title = self.get_element_text("//div[@class='name']/h1")
        company_name = self.get_element_text("//li[@class='company-name']") or "Unknown"

        hr = hr.split(" ")[0].strip()
        company_name = company_name.lstrip("公司名称")
        address = address.strip()
        salary = salary.strip()
        min_salary, max_salary = _extract_salary_range(salary)

        if self.check_exclude(company_name):
            return

        with contextlib.suppress(Exception):
            if self.go_chat_boss(hr, job_title, address):
                global count
                count += 1
                data = {
                    "platform": self.platform,
                    "company": company_name,
                    "job_title": job_title,
                    "min_salary": min_salary,
                    "max_salary": max_salary,
                    "address": address,
                    "category": self.settings.category,
                    "path": job_id,
                    "city": self.settings.expect_city,
                    "creation_time": self.now()
                }
                insert(data)
            logger.info(f"已向 {count} 位boss发送消息")

    def _close(self):
        logger.warning("进程被主动结束")
        super().close()
        os._exit(0)

    @print_log("搜索岗位成功")
    def search_job(self):
        self.fill_element("//input[@class='ipt-search']", self.settings.category)
        self.click_element("//button[@class='btn btn-search']")

    @print_log("正在重新选择城市")
    def choice_city(self):
        if c := self.get_city_code:
            if self.page.url.split("=")[-1] != c and isinstance(self.settings.expect_city, str):
                url = f"{self.page.url.split('city=')[0]}city={c}&page=1"
                self.open(url)
        else:
            raise KeyError("Invalid city")

    @print_log("当前页面处理完成")
    def foreach_job_list(self):
        self.wait_for_element("//ul[@class='job-list-box']")
        job_list_elements = self.find_elements("//li[@class='job-card-wrapper']")
        for el in job_list_elements:
            if self.read_salary(el) is False:
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
            message = msg.format(interview=interview)
            self.fill_element("//div[@class='chat-input']", message)
            self.wait_for_timeout(2)  # 过快发送信息会导致异常
            self.press_key("Enter")
            # self.send_vitae_png()
            self.wait_for_timeout(1.5)  # 过快发送信息会导致异常
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

    @print_log("成功发送简历缩略图")
    def send_vitae_png(self):
        self.upload_file("//input[@type='file'][1]", r"D:\code\python\BigPlayer\sites\applyJob\boss\asset\vitae.png")

    def has_dialog(self):
        return bool(self.find_element("//div[@class='dialog-container']", nullable=True, timeout=2 * 1000))

    def if_chat_ok(self):
        return bool(self.page.get_by_text("已向BOSS发送消息", exact=True))

    def if_been_maximum(self):
        return bool(self.find_element("//p[contains(text(), '请明天再试')]", nullable=True, timeout=2 * 1000))

    def read_salary(self, element):
        try:
            if salary_el := element.query_selector("//span[@class='salary']"):
                salary = _extract_salary_range(salary_el.text_content())
                if self.compare_values(salary) is False:
                    logger.debug(f"岗位薪资范围不符合预期: {salary}￥")
                    return False
                return True
            return False
        except Exception as e:
            traceback.print_exc()
            return True

    def compare_values(self, values):
        var_min, var_max = values
        i = 0
        if var_max > self.settings.max_expect_salary:
            i += 1
        if var_min > self.settings.median_expect_salary or var_min > self.settings.max_expect_salary:
            i += 1

        if i >= 2:
            return False

        if var_min <= self.settings.min_expect_salary:
            return self.settings.median_expect_salary < var_max <= self.settings.max_expect_salary
        if var_min >= self.settings.median_expect_salary:
            if var_min >= self.settings.max_expect_salary:
                return False
            return var_max <= self.settings.max_expect_salary
        return True

    def check_exclude(self, value):
        return any(item in value for item in self.settings.exclude_list)
