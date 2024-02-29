from playwright.sync_api import sync_playwright


class BaseSpider:

    def __init__(self, connect_over_cdp=None):
        """Initialize the spider with optional browser launch arguments."""
        self._connect_over_cdp = connect_over_cdp
        self._playwright = sync_playwright()
        self._driver = self._playwright.start()
        self._browser = None
        self._page = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _init_browser(self, **kwargs):
        if self._browser is None:
            if self._connect_over_cdp:
                self._browser = self._driver.chromium.connect_over_cdp(self._connect_over_cdp)
            else:
                self._browser = self._driver.chromium.launch(**kwargs)

    def close(self):
        """Close the browser and stop the driver."""
        try:
            self._browser.close()
        finally:
            self._driver.stop()
