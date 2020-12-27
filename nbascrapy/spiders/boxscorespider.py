import scrapy
import jsonlines


class BoxscoreSpider(scrapy.Spider):
    name = "boxscore"
    custom_settings = {"FEED_URI": "%(output_dir)s/boxscore.jl"}

    def __init__(self, games_file, output_dir):
        self.games_file = games_file
        self.output_dir = output_dir
        super().__init__()

    def start_requests(self):
        with jsonlines.open(self.games_file) as reader:
            for game in reader:
                if game["boxscore_link"] is None:
                    self.logger.warning(f"Boxscore link is missing for {game}")
                    continue
                url = "https://www.basketball-reference.com" + \
                    game["boxscore_link"]
                yield scrapy.Request(url=url, callback=self.parse)

    def parse_player(self, player):
        profile = {
            "player": player.css("th a::text").extract_first(),
            "player_link": player.css("th a::attr(href)").extract_first(),
        }
        profile.update(
            {
                td.css("td::attr(data-stat)")
                .extract_first(): td.css("td::text")
                .extract_first()
                for td in player.css("td")
            }
        )
        return profile

    def parse(self, response):
        game_url = response.url
        for section in response.css("div.table_wrapper[id*=-game-]"):
            section_id = section.attrib.get("id", "")
            if "basic" in section_id:
                boxscore = "basic"
            elif "advanced" in section_id:
                boxscore = "advanced"

            team = (
                section
                .css("div.section_heading h2::text")
                .extract_first()
            ) or team
            team = team.split("(")[0].strip()

            for i, player in enumerate(
                section.css("table.stats_table tbody tr:not(.thead)")
            ):
                role = "starter" if i < 5 else "reserve"
                profile = self.parse_player(player)
                profile.update(
                    {
                        "game_url": game_url,
                        "team": team,
                        "role": role,
                        "boxscore": boxscore,
                    }
                )
                yield profile
