import pandas as pd


def convert_to_float(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Try to coerce datatypes to float"""
    for col in dataframe:
        try:
            dataframe[col] = dataframe[col].astype(float)
        except ValueError:
            pass
        except TypeError:
            pass
    return dataframe