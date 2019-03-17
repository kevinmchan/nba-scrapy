from nbascrapy.parser import BoxscoreParser


if __name__ == "__main__":
    basic_boxscore_parser = BoxscoreParser(filename="data/boxscore.jl", boxscore_type="basic")
    basic_boxscore_parser.to_parquet(output="data/basic_boxscore.parquet")
    print(basic_boxscore_parser.to_dataframe())

    adv_boxscore_parser = BoxscoreParser(filename="data/boxscore.jl", boxscore_type="advanced")
    adv_boxscore_parser.to_parquet(output="data/adv_boxscore.parquet")
    print(adv_boxscore_parser.to_dataframe())
