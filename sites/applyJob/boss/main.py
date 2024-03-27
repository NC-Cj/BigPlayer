from sites.applyJob.boss.src.spider import BossSite

if __name__ == '__main__':
    with BossSite() as site:
        site.run()
