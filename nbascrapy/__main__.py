import os
import logging
from datetime import datetime
import argparse
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings


if not os.path.exists("logs"):
    os.makedirs("logs")
logfile = "logs/scrapy_{now}.log".format(
    now=datetime.utcnow().strftime("%Y%m%d%H%M%S"))
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(logfile),
        logging.StreamHandler()
    ]
)
runner = CrawlerRunner(get_project_settings())


parser = argparse.ArgumentParser(description="Scrape nba stats")
parser.add_argument(
    "--min",
    action="store",
    type=int,
    help="Minimum season to parse boxscores",
)
parser.add_argument(
    "--max",
    action="store",
    type=int,
    help="Maximum season to parse boxscores"
)
args = parser.parse_args()


@defer.inlineCallbacks
def crawl(min_season, max_season):
    yield runner.crawl("season")
    yield runner.crawl(
        "game",
        filename="data/season.jl",
        min_season=min_season,
        max_season=max_season,
    )
    yield runner.crawl("boxscore", filename="data/game.jl")
    yield runner.crawl("player")
    reactor.stop()


if __name__ == "__main__":
    min_season = f"{args.min}-{(args.min + 1) % 100}"
    max_season = f"{args.max}-{(args.max + 1) % 100}"
    crawl(min_season=min_season, max_season=max_season)
    reactor.run()
