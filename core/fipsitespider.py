import contextlib
import datetime
import os
from typing import Optional, Any, Union

from playwright.sync_api import ElementHandle, Page
from playwright.sync_api import TimeoutError as playTimeoutError

from core import utils
from core.basespider import BaseSpider
from core.utils import validate_action


class FipSiteSpider(BaseSpider):

    def __init__(self, connect_over_cdp):
        super().__init__(connect_over_cdp)
        self._ctx = None
        self.page: Optional[Page] = None

    @staticmethod
    def now():
        datetime.datetime.now()

    def init_site(self, **kwargs):
        if self._ctx is None:
            self._init_browser(**kwargs)

        self._ctx = self._browser.contexts[0]
        self.page = self._ctx.new_page()

    def run(self):
        pass

    def parse(self):
        pass

    def cleanup(self):
        pass

    def click_popup(self, element, timeout=5000):
        element.click()
        return self.page.wait_for_event('popup', timeout=timeout)

    def open(self, url, **kwargs):
        """Open a new page with the given URL."""
        # self.page = self.browser.new_page()
        self.page.goto(url, **kwargs)

    def _wait_for_selector(self, target: Union[str, ElementHandle], **kwargs) -> Optional[ElementHandle]:
        if isinstance(target, ElementHandle):
            return target

        with contextlib.suppress(playTimeoutError):
            return self.page.wait_for_selector(target, **kwargs)

    def find_element(self, selector, *, wait=True, nullable=False, **kwargs) -> Optional[ElementHandle]:
        """通过选择器查找元素"""
        if wait:
            element = self._wait_for_selector(selector, **kwargs)
        else:
            element = self.page.query_selector(selector)
        return utils.validate_element_presence(nullable, element, selector)

    def find_elements(self, selector, nullable=False) -> list[Optional[ElementHandle]]:
        """通过选择器查找所有匹配的元素"""
        element = self.page.query_selector_all(selector)
        return utils.validate_element_presence(nullable, element, selector)

    def press_key(self, key):
        self.page.keyboard.press(key)

    def wait_for_element(self, selector, timeout=10000, allow_exceptions=False) -> Optional[ElementHandle]:
        """Waiting element"""
        try:
            return self.page.wait_for_selector(selector, timeout=timeout)
        except playTimeoutError as e:
            if allow_exceptions:
                return None
            else:
                raise e

    def wait_for_element_to_be_visible(self, selector, timeout=10) -> ElementHandle:
        """Waiting element"""
        return self.page.wait_for_selector(selector, state='visible', timeout=timeout)

    def wait_for_element_to_be_hidden(self, selector, timeout=10) -> ElementHandle:
        """Waiting element"""
        return self.page.wait_for_selector(selector, state='hidden', timeout=timeout)

    @validate_action
    def click_element(self, target, **kwargs) -> Optional[ElementHandle]:
        if element := self._wait_for_selector(target, **kwargs):
            element.click()
        return element

    @validate_action
    def get_element_text(self, target, **kwargs) -> Optional[str]:
        if element := self._wait_for_selector(target, **kwargs):
            return element.text_content()

    @validate_action
    def get_element_attribute(self, target, attribute, **kwargs) -> Optional[str]:
        if element := self._wait_for_selector(target, **kwargs):
            return element.get_attribute(attribute)

    @validate_action
    def double_click_element(self, target, **kwargs) -> Optional[ElementHandle]:
        if element := self._wait_for_selector(target, **kwargs):
            element.dblclick()
        return element

    @validate_action
    def fill_element(self, target, text, **kwargs) -> Optional[ElementHandle]:
        if element := self._wait_for_selector(target, **kwargs):
            element.fill(text)
        return element

    @validate_action
    def upload_file(self, target, file_path, **kwargs) -> Optional[ElementHandle]:
        if element := self._wait_for_selector(target, **kwargs):
            element.set_input_files(file_path)
        return element

    def click_element_and_switch_page(self, target, reset_page=True) -> Optional[Union[Page, ElementHandle]]:
        """单击某个元素并切换到新页面"""
        if self.click_element(target):
            self.page.wait_for_event('popup')

            if not reset_page:
                return self.page.context.pages[-1]
            self.switch_page()

    def take_screenshot(self, path) -> bytes:
        return self.page.screenshot(path)

    def execute_script(self, script) -> Any:
        """在页面上执行脚本。脚本可以是JavaScript代码字符串，也可以是JavaScript文件的路径"""
        if os.path.isfile(script):
            with open(script, 'r') as file:
                script = file.read()
        return self.page.evaluate(script)

    def scroll(self, x, y):
        self.page.evaluate(f"window.scrollBy({x}, {y})")

    def switch_page(self, page_index=-1):
        self.page = self.page.context.pages[page_index]
        return self.page

    def go_back(self):
        """返回上一页"""
        self.page.go_back()

    def close_current_page(self):
        """关闭当前页面并切换到下一页

        如果上下文中有多个页面，它会关闭当前页面并以循环方式切换到下一个页面。
        如果只有一个页面，它将创建一个新页面
        """
        if len(self._ctx.pages) > 1:
            # Switch to the next page if it exists
            next_page_index = (self._ctx.pages.index(self.page) + 1) % len(
                self._ctx.pages
            )
            # Close the current page
            self._ctx.pages[self._ctx.pages.index(self.page)].close()
            # Switch to the next page
            self.page = self._ctx.pages[next_page_index]
        else:
            # If there are no other pages, create a new one
            self.page = self._ctx.new_page()

    def wait_for_timeout(self, seconds):
        self.page.wait_for_timeout(seconds * 1000)
