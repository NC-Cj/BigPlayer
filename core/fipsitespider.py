from core.basespider import BaseSpider


class FipSiteManager(BaseSpider):

    def __init__(self):
        super().__init__()
        self._ctx = None
        self.page = None

    def _init_site(self, **kwargs):
        if self._ctx is None:
            self._init_browser(**kwargs)

        self._ctx = self._browser.contexts[0]
        self.page = self._ctx.new_page()
