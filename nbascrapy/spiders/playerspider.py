import scrapy


class PlayerSpider(scrapy.Spider):
    name = "player"
    custom_settings = {"FEED_URI": "data/player.jl"}
    start_urls = [
        f"https://www.basketball-reference.com/players/{chr(i)}/"
        for i in range(ord("a"), ord("z") + 1)
    ]

    def parse(self, response):
        for player in response.css("#players tbody tr"):
            profile = {
                "player": player.css("th a::text").extract_first(),
                "player_link": player.css("th a::attr(href)").extract_first(),
                "year_min": player.css("td[data-stat=year_min]::text").extract_first(),
                "year_max": player.css("td[data-stat=year_max]::text").extract_first(),
                "pos": player.css("td[data-stat=pos]::text").extract_first(),
                "height": player.css("td[data-stat=height]::text").extract_first(),
                "weight": player.css("td[data-stat=weight]::text").extract_first(),
                "birth_date": player.css(
                    "td[data-stat=birth_date] a::text"
                ).extract_first(),
                "college": player.css("td[data-stat=colleges] a::text").extract_first(),
            }
            yield profile
