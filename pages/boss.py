from core.fipsitespider import BossSite

if __name__ == '__main__':
    with BossSite() as site:
        site.run()
