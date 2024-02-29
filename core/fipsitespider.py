import datetime
import os
from typing import Optional, Any

from playwright.sync_api import ElementHandle, Page

from core import utils
from core.basespider import BaseSpider


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

    def execute_action(self, selector, action):
        """Find an element by its selector and perform the given action on it."""
        element = self.find_element(selector)
        action(element)

    def find_element(self, selector, nullable=False) -> ElementHandle:
        """通过选择器查找元素"""
        element = self.page.query_selector(selector)
        return utils.validate_element_presence(nullable, element, selector)

    def find_elements(self, selector, nullable=False) -> list[ElementHandle]:
        """查找给定选择器匹配的所有元素"""
        element = self.page.query_selector_all(selector)
        return utils.validate_element_presence(nullable, element, selector)

    def click_element(self, selector):
        self.execute_action(selector, lambda element: element.click())

    def double_click_element(self, selector):
        self.execute_action(selector, lambda element: element.dblclick())

    def fill_element(self, selector, text):
        self.execute_action(selector, lambda element: element.fill(text))

    def press_key(self, key):
        self.page.keyboard.press(key)

    def wait_for_element(self, selector, timeout=10000) -> ElementHandle:
        """Waiting element"""
        return self.page.wait_for_selector(selector, timeout=timeout)

    def wait_for_element_to_be_visible(self, selector, timeout=10) -> ElementHandle:
        """Waiting element"""
        return self.page.wait_for_selector(selector, state='visible', timeout=timeout)

    def wait_for_element_to_be_hidden(self, selector, timeout=10) -> ElementHandle:
        """Waiting element"""
        return self.page.wait_for_selector(selector, state='hidden', timeout=timeout)

    def get_element_text(self, selector, nullable=False) -> Optional[str]:
        element = self.find_element(selector, nullable)
        return element.text_content()

    def get_element_attribute(self, selector, attribute) -> Optional[str]:
        element = self.find_element(selector)
        return element.get_attribute(attribute)

    def take_screenshot(self, path) -> bytes:
        return self.page.screenshot(path)

    def upload_file(self, selector, file_path):
        self.execute_action(selector, lambda element: element.set_input_files(file_path))

    def execute_script(self, script) -> Any:
        """Execute a script on the page. The script can be a string of JavaScript code or a path to a JavaScript file."""
        if os.path.isfile(script):
            with open(script, 'r') as file:
                script = file.read()
        return self.page.evaluate(script)

    def scroll(self, x, y):
        self.page.evaluate(f"window.scrollBy({x}, {y})")

    def switch_page(self, page_index=-1):
        self.page = self.page.context.pages[page_index]

    def go_back(self):
        """Go back to the previous page."""
        self.page.go_back()

    def close_current_page(self):
        """Close the current page and switch to another page."""
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

    def click_element_and_switch_page(self, selector, reset_page=True):
        element = self.find_element(selector)
        element.click()

        self.page.wait_for_event('popup')
        if reset_page:
            self.switch_page()
        else:
            return self.page.context.pages[-1]

    def wait_for_timeout(self, seconds):
        self.page.wait_for_timeout(seconds * 1000)
