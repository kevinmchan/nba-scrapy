import scrapy


class SeasonSpider(scrapy.Spider):
    name = "season"
    custom_settings = {"FEED_URI": "%(output_dir)s/season.jl"}
    start_urls = ["https://www.basketball-reference.com/leagues/"]

    def __init__(self, output_dir):
        self.output_dir = output_dir
        super().__init__()

    def parse(self, response):
        for season in response.css("table.stats_table tr:not(.thead)"):
            yield {
                "season": season.css("[data-stat=season] a::text").extract_first(),
                "season_link": season.css(
                    "[data-stat=season] a::attr(href)"
                ).extract_first(),
                "league": season.css("[data-stat=lg_id] a::text").extract_first(),
            }
