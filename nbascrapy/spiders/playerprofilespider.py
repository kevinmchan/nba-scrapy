import scrapy
import jsonlines


class PlayerProfileSpider(scrapy.Spider):
    name = "playerprofile"
    custom_settings = {"FEED_URI": "%(output_dir)s/playerprofile.jl"}

    def __init__(self, players_file, output_dir):
        self.players_file = players_file
        self.output_dir = output_dir
        super().__init__()

    def start_requests(self):
        with jsonlines.open(self.players_file) as reader:
            for player in reader:
                url = "https://www.basketball-reference.com" + player["player_link"]
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        pass
