from abc import ABCMeta, abstractmethod
from typing import List, Optional, Callable, Union
import pandas as pd
from modeling.contracts import method_output_is_same_size


class BaseFeatureGenerator(metaclass=ABCMeta):
    @abstractmethod
    def transform(self, Xs: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError


class RollingAverageStats(BaseFeatureGenerator):
    def __init__(
        self,
        stats: List[str],
        window: int,
        naming_func: Optional[Callable[[str], str]] = None,
    ) -> None:
        """Generates the rolling average of a given set of boxscore stats,
        not including the stats for the current game
        
        Params:
            stats: list of stats to aggregate
            window: number of games to aggregate over
            naming_func: a callable that is applied to name the derived columns
        """
        self.stats = stats
        self.window = window
        self.naming_func = (
            naming_func if naming_func else lambda col: f"{col}_prev_{window}g_avg"
        )

    @method_output_is_same_size(arg_pos=0, kw_name="boxscore_data")
    def transform(
        self, boxscore_data: pd.DataFrame, game_data: pd.DataFrame
    ) -> pd.DataFrame:
        """Apply transformation on input dataframes
        
        Params:
            boxscore_data: a dataframe with player_link, boxscore_link, and stats
            game_data: a dataframe with boxscore_link and date

        Returns:
            output: dataframe with rolling average of specified stats
        """
        merged_dataset = pd.merge(boxscore_data, game_data, on=["boxscore_link"])
        sorted_dataset = merged_dataset.sort_values(by=["player_link", "date"])
        averages = (
            sorted_dataset.groupby(["player_link"])[self.stats]
            .apply(
                lambda x: x.shift(1).rolling(window=self.window, min_periods=1).mean()
            )
            .rename(columns=self.naming_func)
        )
        output = sorted_dataset[["player_link", "boxscore_link"]].join(averages)
        return output


class PerUnitStats(BaseFeatureGenerator):
    def __init__(
        self,
        stats: List[str],
        dividend: str,
        naming_func: Optional[Callable[[str], str]] = None,
    ) -> None:
        """Generates per unit stats by dividing by a given column
        
        Params:
            stats: list of stats to divide
            dividend: name of column to divide by
            naming_func: a callable that is applied to name the derived columns
        """
        self.stats = stats
        self.dividend = dividend
        self.naming_func = (
            naming_func if naming_func else lambda col: f"{col}_per_{dividend}"
        )

    @method_output_is_same_size(0, "data")
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply transformation on input dataframe"""
        output = (
            data[self.stats]
            .divide(data[self.dividend], axis="index")
            .rename(columns=self.naming_func)
            .join(data[["boxscore_link", "player_link"]])
        )
        return output


class Merge(BaseFeatureGenerator):
    def __init__(
        self,
        on: Union[List[str], str],
        how: str = "inner",
        keep: Optional[List[str]] = None,
    ) -> None:
        """Merge two input dataframes
        
        Params:
            on: list of column names, or single column name to join on
            how: type of join {"inner", "left", "outer"}, defaults to inner
            keep: list of columns to keep after joining
        """
        self.on = on
        self.how = how
        self.keep = keep

    def transform(self, left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
        """Merge input dataframes"""
        output = left.merge(right, how=self.how, on=self.on)
        if self.keep is not None:
            output = output[self.keep]
        return output


class SeasonGameCount(BaseFeatureGenerator):
    def __init__(self) -> None:
        """Adds count of number of games played by player in the season"""
        pass

    @method_output_is_same_size(0, "boxscore_data")
    def transform(
        self, boxscore_data: pd.DataFrame, game_data: pd.DataFrame
    ) -> pd.DataFrame:
        """Apply transformation on input dataframe"""
        merged_dataset = pd.merge(boxscore_data, game_data, on=["boxscore_link"])
        output = merged_dataset.sort_values(by=["player_link", "date"]).assign(
            season_game_count=lambda x: x.groupby(
                ["player_link", "season_link", "playoffs"]
            )["date"].rank(method="dense")
        )
        output = output[["player_link", "boxscore_link", "season_game_count"]]
        return output


class GameCount(BaseFeatureGenerator):
    def __init__(self) -> None:
        """Adds count of number of games played by player"""
        pass

    @method_output_is_same_size(0, "boxscore_data")
    def transform(
        self, boxscore_data: pd.DataFrame, game_data: pd.DataFrame
    ) -> pd.DataFrame:
        """Apply transformation on input dataframe"""
        merged_dataset = pd.merge(boxscore_data, game_data, on=["boxscore_link"])
        output = merged_dataset.sort_values(by=["player_link", "date"]).assign(
            game_count=lambda x: x.groupby(["player_link", "playoffs"])["date"].rank(
                method="dense"
            )
        )
        output = output[["player_link", "boxscore_link", "game_count"]]
        return output


class PlayerAge(BaseFeatureGenerator):
    def __init__(self) -> None:
        """Calculates player age in days as of the game date"""
        pass

    @method_output_is_same_size(0, "boxscore_data")
    def transform(
        self,
        boxscore_data: pd.DataFrame,
        game_data: pd.DataFrame,
        player_data: pd.DataFrame,
    ) -> pd.DataFrame:
        """Apply transformation on input dataframes"""
        output = (
            boxscore_data.merge(game_data, on="boxscore_link", how="left")
            .merge(player_data, on="player_link", how="left")
            .assign(age_in_days=lambda x: (x["date"] - x["birth_date"]).dt.days)[
                ["player_link", "boxscore_link", "age_in_days"]
            ]
        )
        return output
