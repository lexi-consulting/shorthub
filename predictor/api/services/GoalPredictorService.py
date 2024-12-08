import statsmodels.api as sm
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
from statsmodels.tools.sm_exceptions import ValueWarning
from understat.api.models.Team import Team
from understat.api.models.Match import Match
from django.db import models
from predictor.api.models.TrainedModel import TrainedModel
import json
class GoalPredictorService:
    def __init__(self):
        self.seasons_data = None
        self.model_under = None
        self.model_over = None
        self.model_both = None

    def get_regression_data(self):

        data = pd.DataFrame()
        teams = Team.objects.all()

        for team in teams:
            matches = Match.objects.filter(models.Q(home_team=team) | models.Q(away_team=team)).order_by('datetime')
            team_data = pd.DataFrame.from_records(matches.values(
                'match_id', 'home_team__title', 'away_team__title', 'home_goals', 
                'away_goals', 'home_xg', 'away_xg', 'datetime'
            ))
            if not team_data.empty:
                team_data['team'] = team.title
                team_data['opp'] = team_data.apply(
                    lambda row: row['home_team__title'] if row['home_team__title'] != team.title else row['away_team__title'], axis=1
                )
                team_data['goals'] = team_data.apply(
                    lambda row: row['home_goals'] if row['home_team__title'] == team.title else row['away_goals'], axis=1
                )
                team_data['opp_goals'] = team_data.apply(
                    lambda row: row['away_goals'] if row['home_team__title'] == team.title else row['home_goals'], axis=1
                )
                team_data['xG'] = team_data.apply(
                    lambda row: row['home_xg'] if row['home_team__title'] == team.title else row['away_xg'], axis=1
                )
                team_data['opp_xG'] = team_data.apply(
                    lambda row: row['away_xg'] if row['home_team__title'] == team.title else row['home_xg'], axis=1
                )
                data = pd.concat([data, team_data])
            break

        data["tot_xG"] = data["xG"] + data["opp_xG"]
        data["under"] = data["tot_xG"] < 3
        data["over"] = data["tot_xG"] > 3
        data["both"] = (data["goals"] > 0) & (data["opp_goals"] > 0)
        self.seasons_data = data
        return json.loads(data.to_json(orient='records'))

    def logistic_regression(self):
        warnings.simplefilter("ignore", category=(ValueWarning, UserWarning))
        X = sm.add_constant(self.seasons_data["tot_xG"])

        y_under = self.seasons_data["under"]
        self.model_under = sm.Logit(y_under, X).fit()

        y_over = self.seasons_data["over"]
        self.model_over = sm.Logit(y_over, X).fit()

        y_both = self.seasons_data["both"]
        self.model_both = sm.Logit(y_both, X).fit()

        self._save_model_to_db('under', self.model_under)
        self._save_model_to_db('over', self.model_over)
        self._save_model_to_db('both', self.model_both)

    def _save_model_to_db(self, model_name: str, model):
        """Save the trained model to the database."""
        TrainedModel.objects.update_or_create(
            model_name=model_name,
            defaults={
                'coefficients': model.params.to_dict(),
                'intercept': model.params['const']
            }
        )

    def predict_week(self):
        team_ids = self.understat.get_teams()
        current_data = pd.concat(
            [self.understat.get_time_series(team_id, "2023") for team_id in team_ids]
        )

        today = datetime.today()
        end_of_week = today + timedelta(days=7)
        week = current_data[
            (current_data["datetime"] > today)
            & (current_data["datetime"] < end_of_week)
        ]

        week_forecasts = week.copy()
        week_forecasts["forecast_xG"] = week_forecasts["xG"]
        week_forecasts["forecast_opp_xG"] = week_forecasts["opp_xG"]

        week_forecasts["pred_under"] = self.model_under.predict(
            sm.add_constant(week_forecasts["forecast_xG"])
        )
        week_forecasts["pred_over"] = self.model_over.predict(
            sm.add_constant(week_forecasts["forecast_xG"])
        )
        week_forecasts["pred_both"] = self.model_both.predict(
            sm.add_constant(week_forecasts["forecast_xG"])
        )

        week_forecasts[["pred_under", "pred_over", "pred_both"]] = np.exp(
            week_forecasts[["pred_under", "pred_over", "pred_both"]]
        ) / (1 + np.exp(week_forecasts[["pred_under", "pred_over", "pred_both"]]))

        threshold = 0
        potential_bets = week_forecasts[
            (week_forecasts["pred_under"] > threshold)
            | (week_forecasts["pred_over"] > threshold)
            | (week_forecasts["pred_both"] > threshold)
        ]

        potential_bets = potential_bets.sort_values(
            by=["pred_under", "pred_over", "pred_both"], ascending=False
        )
        potential_bets = potential_bets[
            ["id", "under", "over", "both", "pred_under", "pred_over", "pred_both"]
        ]

        return potential_bets
