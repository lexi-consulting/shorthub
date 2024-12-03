import understat.api.Understat as Understat
import statsmodels.api as sm
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
from statsmodels.tools.sm_exceptions import ValueWarning


class GoalPredictor:
    model_under = None
    model_over = None
    model_both = None

    def __init__(self):
        self.understat = Understat.Understat()
        self.understat.read_data()
        self.seasons_data = None

    def get_regression_data(self):
        teams = self.understat.get_teams()
        seasons = self.understat.SEASONS
        # we need to get the time series for every team and season combination, and then extract the relevant columns
        # matchID,team ,opp ,home, goals, opp_goals, xG, opp_xG, under , over ,boh,matchNo, sequential_match_no
        # forecast, home_forecast, away_forecast
        # then we need to add them all to one dataframe
        data = pd.DataFrame()
        for team in teams:
            for season in seasons:
                team_data = self.understat.get_time_series(team, season)
                if team_data is not None:
                    data = pd.concat(
                        [
                            data,
                            team_data[
                                [
                                    "id",
                                    "team",
                                    "opp",
                                    "home",
                                    "goals",
                                    "opp_goals",
                                    "xG",
                                    "opp_xG",
                                    "under",
                                    "over",
                                    "both",
                                    "sequential_match_no",
                                ]
                            ],
                        ]
                    )
        data["tot_xG"] = data["xG"] + data["opp_xG"]
        self.seasons_data = data

    def logistic_regression(self):
        warnings.simplefilter("ignore", category=(ValueWarning, UserWarning))
        # Assuming that 'forecast' is the independent variable for all three models
        X = sm.add_constant(self.seasons_data["tot_xG"])

        # Create model for 'under'
        y_under = self.seasons_data["under"]
        self.model_under = sm.Logit(y_under, X).fit()

        # Create model for 'over'
        y_over = self.seasons_data["over"]
        self.model_over = sm.Logit(y_over, X).fit()

        # Create model for 'both'
        y_both = self.seasons_data["both"]
        self.model_both = sm.Logit(y_both, X).fit()

    def predict_week(self):
        # Create current_data dataframe
        team_ids = self.understat.get_teams()
        current_data = pd.concat(
            [self.understat.get_time_series(team_id, "2023") for team_id in team_ids]
        )

        # Create week dataframe
        today = datetime.today()
        end_of_week = today + timedelta(days=7)
        week = current_data[
            (current_data["datetime"] > today)
            & (current_data["datetime"] < end_of_week)
        ]

        # Update week.forecasts dataframe
        week_forecasts = week.copy()
        week_forecasts["forecast_xG"] = week_forecasts["xG"]
        week_forecasts["forecast_opp_xG"] = week_forecasts["opp_xG"]

        return week_forecasts
        # Predict probabilities
        week_forecasts["pred_under"] = self.model_under.predict(
            sm.add_constant(week_forecasts["forecast_xG"])
        )
        week_forecasts["pred_over"] = self.model_over.predict(
            sm.add_constant(week_forecasts["forecast_xG"])
        )
        week_forecasts["pred_both"] = self.model_both.predict(
            sm.add_constant(week_forecasts["forecast_xG"])
        )

        # Convert log-odds to probabilities
        week_forecasts[["pred_under", "pred_over", "pred_both"]] = np.exp(
            week_forecasts[["pred_under", "pred_over", "pred_both"]]
        ) / (1 + np.exp(week_forecasts[["pred_under", "pred_over", "pred_both"]]))
        return week_forecasts
        # Identify potential bets
        threshold = 0
        potential_bets = week_forecasts[
            (week_forecasts["pred_under"] > threshold)
            | (week_forecasts["pred_over"] > threshold)
            | (week_forecasts["pred_both"] > threshold)
        ]

        # Sort and select columns
        potential_bets = potential_bets.sort_values(
            by=["pred_under", "pred_over", "pred_both"], ascending=False
        )
        potential_bets = potential_bets[
            ["matchID", "under", "over", "both", "pred_under", "pred_over", "pred_both"]
        ]

        return potential_bets
