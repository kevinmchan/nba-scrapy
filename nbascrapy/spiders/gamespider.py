import scrapy
import jsonlines


class GameSpider(scrapy.Spider):
    name = "game"
    custom_settings = {"FEED_URI": "data/game.jl"}

    def __init__(self, filename, min_season=None, max_season=None):
        self.datafile = filename
        self.min_season = min_season or "0000-01"
        self.max_season = max_season or "9998-99"

    def start_requests(self):
        with jsonlines.open(self.datafile) as reader:
            for season in reader:
                if (
                    season["season"] < self.min_season
                    or season["season"] > self.max_season
                ):
                    continue
                url = "https://www.basketball-reference.com" + season["season_link"]
                self.logger.debug(f"Requesting season {url}")
                yield scrapy.Request(url=url, callback=self.parse_season)

    def parse_season(self, response):
        schedule_link = response.css(
            "#inner_nav a[href*=_games]::attr(href)"
        ).extract_first()
        self.logger.debug(f"Requesting season schedule {schedule_link}")
        yield scrapy.Request(
            url="https://www.basketball-reference.com" + schedule_link,
            callback=self.parse,
            meta={"season_url": response.url},
        )

    def parse(self, response):
        month_filter = response.css("div.filter")
        for link in month_filter.css("a"):
            self.logger.debug(f"Requesting month schedule {link}")
            yield response.follow(
                url=link,
                callback=self.parse_monthly_schedule,
                meta={"season_url": response.meta["season_url"]},
            )

    def parse_monthly_schedule(self, response):
        schedule = response.css("table#schedule")
        season_url = response.meta["season_url"]
        for row in schedule.css("tbody tr:not(.thead)"):
            data = {
                "date": row.css("[data-stat=date_game] a::text").extract_first(),
                "start": row.css("[data-stat=game_start_time]::text").extract_first(),
                "visitor": row.css(
                    "[data-stat=visitor_team_name] a::text"
                ).extract_first(),
                "visitor_link": row.css(
                    "[data-stat=visitor_team_name] a::attr(href)"
                ).extract_first(),
                "visitor_pts": row.css("[data-stat=visitor_pts]::text").extract_first(),
                "home": row.css("[data-stat=home_team_name] a::text").extract_first(),
                "home_link": row.css(
                    "[data-stat=home_team_name] a::attr(href)"
                ).extract_first(),
                "home_pts": row.css("[data-stat=home_pts]::text").extract_first(),
                "boxscore_link": row.css(
                    "[data-stat=box_score_text] a::attr(href)"
                ).extract_first(),
                "overtime": row.css("[data-stat=overtimes]::text").extract_first(),
                "attendance": row.css("[data-stat=attendance]::text").extract_first(),
                "notes": row.css("[data-stat=game_remarks]::text").extract_first(),
                "season_link": season_url,
            }
            self.logger.debug("Parsing game {}".format(data["boxscore_link"]))
            yield data
