from sites.hot.zhihu.src.spider import ZhihuSite

if __name__ == '__main__':
    with ZhihuSite() as site:
        site.run()
