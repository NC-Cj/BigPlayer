from sites.hot.jujin.src.spider import JuejinSite

if __name__ == '__main__':
    with JuejinSite() as site:
        site.run()
