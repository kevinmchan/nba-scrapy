from abc import abstractmethod, ABCMeta
import jsonlines
import pandas as pd
from nbascrapy.util import convert_to_float


class BaseParser(metaclass=ABCMeta):
    """Abstract base class for data parsers

    Params:
        filename: name of file to parse
    """
    def __init__(self, filename: str):
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    @abstractmethod
    def to_dataframe(self) -> pd.DataFrame:
        """Abstract method for returning data as dataframe"""
        pass

    @abstractmethod
    def to_parquet(self, output: str) -> None:
        """Abstract method for outputting data in parquet format

        Params:
            output: name of output file
        """
        pass


class BoxscoreParser(BaseParser):
    """Parses boxscore jsonlines file

    Params:
        filename: name of file to parse
        type: type of boxscore statistics to return; value in {"basic", "advanced"}
    """
    def __init__(self, filename: str, boxscore_type: str):
        super().__init__(filename)
        assert boxscore_type in ("basic", "advanced"), "boxscore_type must be 'basic' or 'advanced'"
        self.boxscore_type = boxscore_type

    def to_dataframe(self) -> pd.DataFrame:
        with jsonlines.open(self.filename) as reader:
            return (
                pd.DataFrame(
                    list(filter(lambda x: x.get('boxscore') == self.boxscore_type, iter(reader)))
                )
                .pipe(convert_to_float)
            )

    def to_parquet(self, output: str) -> None:
        self.to_dataframe().to_parquet(output)
