import pandas as pd


def load_boxscore_data() -> pd.DataFrame:
    """Load basic boxscore dataset
    
    Returns:
        dataframe: dataset containing basic game stats, unique to each game and player
    """
    basic_boxscores_df = pd.read_parquet("data/basic_boxscore.parquet")
    basic_boxscores_df = basic_boxscores_df.rename(
        columns={"game_url": "boxscore_link"}
    )

    # there are a few games with duplicated boxscore records -> remove duplicates
    basic_boxscores_df = basic_boxscores_df.sort_values(by=["boxscore_link", "minutes"])
    basic_boxscores_df = basic_boxscores_df[
        ~basic_boxscores_df.eval("boxscore_link + player_link + team").duplicated()
    ].copy()

    return basic_boxscores_df


def load_adv_boxscore_data() -> pd.DataFrame:
    """Load advanced boxscore dataset
    
    Returns:
        dataframe: dataset containing advanced game stats, unique to each game and player
    """
    basic_boxscores_df = pd.read_parquet("data/adv_boxscore.parquet")
    basic_boxscores_df = basic_boxscores_df.rename(
        columns={"game_url": "boxscore_link"}
    )

    # there are a few games with duplicated boxscore records -> remove duplicates
    basic_boxscores_df = basic_boxscores_df.sort_values(by=["boxscore_link", "minutes"])
    basic_boxscores_df = basic_boxscores_df[
        ~basic_boxscores_df.eval("boxscore_link + player_link + team").duplicated()
    ].copy()

    return basic_boxscores_df


def load_season_data() -> pd.DataFrame:
    """Load season dataset
    
    Returns:
        dataframe: dataset containing list of seasons, unique to year and league
    """
    seasons_df = pd.read_parquet("data/season.parquet")

    # convert season to integer
    seasons_df.season = seasons_df.season.str.split("-").str[0].astype(int)
    return seasons_df


def load_team_game_data() -> pd.DataFrame:
    """Load team game dataset
    
    Returns:
        dataframe: dataset containing game info, unique to each game and team
    """
    team_games_df = pd.read_parquet("data/normalized_games.parquet")

    team_games_df = team_games_df[
        ["boxscore_link", "team", "team_link", "pts", "location"]
    ]
    return team_games_df


def load_game_data() -> pd.DataFrame:
    """Load game dataset
    
    Returns:
        dataframe: dataset containing game info, unique to each game
    """
    games_df = pd.read_parquet("data/normalized_games.parquet")

    game_cols = [
        "boxscore_link",
        "season_link",
        "start",
        "notes",
        "overtime",
        "attendance",
        "date",
        "playoffs",
    ]

    games_df = games_df[game_cols].drop_duplicates()

    # duplicates due to mismatch in playoffs assignment,
    # resulting from some teams having shortened seasons
    duplicated_games = games_df.loc[
        games_df.boxscore_link.duplicated(), "boxscore_link"
    ]
    games_df.loc[games_df.boxscore_link.isin(duplicated_games), "playoffs"] = True
    games_df = games_df.drop_duplicates()

    return games_df


def _height_string_to_float(series):
    return (
        series.str.split("-", expand=True)
        .apply(lambda x: x.astype(float))
        .rename(columns={0: "feet", 1: "inches"})
        .eval("feet + inches/12")
    )


def load_player_data() -> pd.DataFrame:
    """Load player data

    Returns:
        dataframe: dataset containing each player and their attributes
    """
    players_df = pd.read_parquet("data/player.parquet")

    # convert height to single numeric column
    players_df.height = _height_string_to_float(players_df.height)

    # convert birth date to datetime
    players_df.birth_date = pd.to_datetime(players_df.birth_date)

    # encode player position
    for pos in ["F", "C", "G"]:
        players_df[f"pos_{pos.lower()}"] = (
            players_df.pos.fillna("").str.contains(pos).astype(int)
        )

    # count number of positions, each player is listed as playing
    players_df["n_pos"] = players_df[["pos_f", "pos_c", "pos_g"]].sum(axis=1)

    # scale player encoding such that the sum of position played == 1
    for pos in ["F", "C", "G"]:
        players_df[f"pos_{pos.lower()}_scaled"] = (
            players_df[f"pos_{pos.lower()}"] / players_df["n_pos"]
        )

    return players_df
