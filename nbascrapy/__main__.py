from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
import logging
from datetime import datetime


logfile = "logs/scrapy_{now}.log".format(now=datetime.utcnow().strftime("%Y%m%d%H%M%S"))
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(logfile),
        logging.StreamHandler()
    ]
)
runner = CrawlerRunner(get_project_settings())


@defer.inlineCallbacks
def crawl():
    yield runner.crawl("season")
    yield runner.crawl("game", filename="data/season.jl", min_season="2018-19", max_season="2018-19")
    yield runner.crawl("boxscore", filename="data/game.jl")
    yield runner.crawl("player")
    reactor.stop()


if __name__ == "__main__":
    crawl()
    reactor.run()
