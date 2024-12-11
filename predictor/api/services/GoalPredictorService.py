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
from typing import List, Tuple
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Flatten, Dense, Input
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import accuracy_score
import tensorflow as tf

class GoalPredictorService:
    def __init__(self):
        self.seasons_data = None
        self.model_under = None
        self.model_over = None
        self.model_both = None
        self.model = None

    @staticmethod
    def get_last_5_matches(team, match_date, home=True) -> List[Match]:
        """Fetch the last 5 matches for a team, either home or away."""
        if home:
            matches = Match.objects.filter(
                home_team=team, datetime__lt=match_date
            ).order_by('-datetime')[:5]
        else:
            matches = Match.objects.filter(
                away_team=team, datetime__lt=match_date
            ).order_by('-datetime')[:5]
        return matches

    def get_regression_data(self) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        data = []
        matches_with_results = Match.objects.filter(is_result=True).order_by('datetime')
        print("Total matches with results: ", len(matches_with_results))
        # For testing, only use 1000 matches
        matches_with_results = matches_with_results[:1000]
        count = 0
        for match in matches_with_results:
            count += 1
            if count % 500 == 0:
                print("Processed ", count, " matches")
            home_team = match.home_team
            away_team = match.away_team
            match_date = match.datetime

            # Get last 5 matches for both teams
            home_team_data = self.get_last_5_matches(home_team, match_date, home=True)
            home_team_away_data = self.get_last_5_matches(home_team, match_date, home=False)
            away_team_data = self.get_last_5_matches(away_team, match_date, home=True)
            away_team_away_data = self.get_last_5_matches(away_team, match_date, home=False)

            # Ensure we have enough data and the last match was within a month
            if (len(home_team_data) < 5 or len(home_team_away_data) < 5 or
                len(away_team_data) < 5 or len(away_team_away_data) < 5):
                continue

            # Check if the last match for each team was within a month
            if (home_team_data[0].datetime < match_date - timedelta(days=30) or
                home_team_away_data[0].datetime < match_date - timedelta(days=30) or
                away_team_data[0].datetime < match_date - timedelta(days=30) or
                away_team_away_data[0].datetime < match_date - timedelta(days=30)):
                continue

            # Create the 5x5x2 matrix with days since the match
            predictor_matrix = np.array([
                [m.home_xg, m.away_xg, m.home_goals, m.away_goals, (match_date - m.datetime).days] for m in home_team_data
            ] + [
                [m.home_xg, m.away_xg, m.home_goals, m.away_goals, (match_date - m.datetime).days] for m in home_team_away_data
            ] + [
                [m.home_xg, m.away_xg, m.home_goals, m.away_goals, (match_date - m.datetime).days] for m in away_team_data
            ] + [
                [m.home_xg, m.away_xg, m.home_goals, m.away_goals, (match_date - m.datetime).days] for m in away_team_away_data
            ])

            predictor_matrix = predictor_matrix.reshape(10, 5, 2)

            # Create the outcome vector
            outcome_vector = np.array([
                int(match.home_goals + match.away_goals > 3),
                int(match.home_goals + match.away_goals < 3),
                int(match.home_goals > 0 and match.away_goals > 0)
            ])

            data.append((predictor_matrix, outcome_vector))

        # Split data into training and test sets
        train_size = int(0.8 * len(data))
        train_data = data[:train_size]
        test_data = data[train_size:]

        return train_data, test_data

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

    def train_and_test_cnn(self):
        # Get the training and test data
        train_data, test_data = self.get_regression_data()

        # Separate predictors and outcomes
        X_train = np.array([x for x, _ in train_data])
        y_train = np.array([y for _, y in train_data])
        X_test = np.array([x for x, _ in test_data])
        y_test = np.array([y for _, y in test_data])

        # One-hot encode the outcome vectors
        y_train_encoded = to_categorical(y_train[:, 0], num_classes=3)  # Use only the first column
        y_test_encoded = to_categorical(y_test[:, 0], num_classes=3)    # Use only the first column

        # Define the CNN model with an Input layer
        self.model = Sequential([
            Input(shape=(10, 5, 2)),
            Conv2D(64, kernel_size=(3, 3), activation='relu', padding='same'),
            Conv2D(128, kernel_size=(3, 3), activation='relu', padding='same'),
            Flatten(),
            Dense(1024, activation='relu'),
            Dense(256, activation='relu'),
            Dense(32, activation='relu'),
            Dense(3, activation='softmax')
        ])

        # Compile the model
        self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

        # Train the model
        self.model.fit(X_train, y_train_encoded, epochs=10, batch_size=32, validation_split=0.2)  # Increase epochs

        # Evaluate the model
        y_pred_encoded = self.model.predict(X_test)
        y_pred = np.argmax(y_pred_encoded, axis=1)
        y_true = np.argmax(y_test_encoded, axis=1)

        # Calculate accuracy
        accuracy = accuracy_score(y_true, y_pred)
        print(f"Test Accuracy: {accuracy * 100:.2f}%")

        # List available devices
        print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

        # Return a dictionary with metrics instead of the model
        return {
            'accuracy': float(accuracy),  # Convert to float for JSON serialization
            'gpu_count': len(tf.config.list_physical_devices('GPU')),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
