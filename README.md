# NBA Scrapy

This project provides tools for scraping NBA data.

## Setup

Create python environment:

```bash
conda env create -f environment.yml -n nbascrapy
conda activate nbascrapy
```

## Download NBA data

To download NBA data using the scraper:

```bash
python -m nbascrapy --min=2018 --max=2018
```

The min and max arguments provide bounds for the earliest and latest seasons to include in game and boxscore results.

This will generate the following results in a `data/` directory:

- season.jl: list of all nba seasons
- player.jl: list of players to have played in the nba
- game.jl: list of games within the min and max seasons provided
- boxscore.jl: basic and advanced boxscore stats for each player and game within the min/max season range provided
