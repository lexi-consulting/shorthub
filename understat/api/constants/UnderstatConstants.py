class UnderstatConstants:
    """Constants used for Understat API interactions."""
    
    BASE_URL: str = "https://understat.com/league/"
    LEAGUES: list[str] = ["EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]
    SEASONS: list[str] = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]