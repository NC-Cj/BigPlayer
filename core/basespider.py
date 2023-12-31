import os
from typing import Optional, Any

from playwright.sync_api import sync_playwright, ElementHandle


class BaseSpider:

    def __init__(self, connect_over_cdp=None, **kwargs):
        """Initialize the spider with optional browser launch arguments."""
        self._playwright = sync_playwright()
        self._driver = self._playwright.start()

        if connect_over_cdp:
            self.browser = self._driver.chromium.connect_over_cdp(connect_over_cdp)
        else:
            self.browser = self._driver.chromium.launch(**kwargs)
        self.ctx = self.browser.contexts[0]
        self.page = self.ctx.new_page()

    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context related to this object."""
        self.close()

    @staticmethod
    def element_query(element, selector) -> ElementHandle:
        return element.query_selector(selector)

    def open(self, url):
        """Open a new page with the given URL."""
        # self.page = self.browser.new_page()
        self.page.goto(url)

    def perform_action_on_element(self, selector, action):
        """Find an element by its selector and perform the given action on it."""
        element = self.find_element(selector)
        action(element)

    def find_element(self, selector, nullable=False) -> ElementHandle:
        """Find an element by its selector. If nullable is False and the element does not exist, raise an exception."""
        element = self.page.query_selector(selector)
        if nullable:
            return element
        if element is None:
            raise ValueError(f"No element found for selector: {selector}")

        return element

    def find_elements(self, selector) -> list[ElementHandle]:
        """Find all elements matching the given selector."""
        return self.page.query_selector_all(selector)

    def click_element(self, selector):
        self.perform_action_on_element(selector, lambda element: element.click())

    def double_click_element(self, selector):
        self.perform_action_on_element(selector, lambda element: element.dblclick())

    def fill_element(self, selector, text):
        self.perform_action_on_element(selector, lambda element: element.fill(text))

    def press_key(self, key):
        self.page.keyboard.press(key)

    def wait_for_element(self, selector, timeout=10) -> ElementHandle:
        """Waiting element"""
        return self.page.wait_for_selector(selector, timeout=timeout)

    def wait_for_element_to_be_visible(self, selector, timeout=10) -> ElementHandle:
        """Waiting element"""
        return self.page.wait_for_selector(selector, state='visible', timeout=timeout)

    def wait_for_element_to_be_hidden(self, selector, timeout=10) -> ElementHandle:
        """Waiting element"""
        return self.page.wait_for_selector(selector, state='hidden', timeout=timeout)

    def get_element_text(self, selector) -> Optional[str]:
        """Get element Text."""
        element = self.find_element(selector)
        return element.text_content()

    def get_element_attribute(self, selector, attribute) -> Optional[str]:
        element = self.find_element(selector)
        return element.get_attribute(attribute)

    def take_screenshot(self, path) -> bytes:
        return self.page.screenshot(path)

    def upload_file(self, selector, file_path):
        self.perform_action_on_element(selector, lambda element: element.set_input_files(file_path))

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
        if len(self.ctx.pages) > 1:
            # Switch to the next page if it exists
            next_page_index = (self.ctx.pages.index(self.page) + 1) % len(self.ctx.pages)
            # Close the current page
            self.ctx.pages[self.ctx.pages.index(self.page)].close()
            # Switch to the next page
            self.page = self.ctx.pages[next_page_index]
        else:
            # If there are no other pages, create a new one
            self.page = self.ctx.new_page()

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

    def close(self):
        """Close the browser and stop the driver."""
        try:
            self.browser.close()
        finally:
            self._driver.stop()
