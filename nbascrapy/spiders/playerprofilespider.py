import scrapy
import jsonlines


class PlayerProfileSpider(scrapy.Spider):
    name = "playerprofile"
    custom_settings = {"FEED_URI": "data/playerprofile.jl"}

    def __init__(self, filename):
        self.datafile = filename

    def start_requests(self):
        with jsonlines.open(self.datafile) as reader:
            for player in reader:
                url = "https://www.basketball-reference.com" + player["player_link"]
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        pass
