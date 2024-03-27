from sites.applyJob.zhilian.src.spider import ZhilinSite

if __name__ == '__main__':
    with ZhilinSite() as site:
        site.run()
