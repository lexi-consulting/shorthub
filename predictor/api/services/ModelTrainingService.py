import statsmodels.api as sm
import warnings
from statsmodels.tools.sm_exceptions import ValueWarning
from predictor.api.models.TrainedModel import TrainedModel
from predictor.api.services.GoalPredictorService import GoalPredictorService

class ModelTrainingService:
    def __init__(self):
        self.predictor = GoalPredictorService()

    def train_model(self) -> dict:
        """Train the logistic regression model and save it to the database."""
        regression_data = self.predictor.get_regression_data()
        
        warnings.simplefilter("ignore", category=(ValueWarning, UserWarning))
        X = sm.add_constant(self.predictor.seasons_data["tot_xG"])

        y_under = self.predictor.seasons_data["under"]
        model_under = sm.Logit(y_under, X).fit()

        y_over = self.predictor.seasons_data["over"]
        model_over = sm.Logit(y_over, X).fit()

        y_both = self.predictor.seasons_data["both"]
        model_both = sm.Logit(y_both, X).fit()

        self._save_model_to_db('under', model_under)
        self._save_model_to_db('over', model_over)
        self._save_model_to_db('both', model_both)
        
        return {"status": "success", "message": "Model trained and saved successfully."}

    def _save_model_to_db(self, model_name: str, model) -> None:
        """Save the trained model to the database."""
        TrainedModel.objects.update_or_create(
            model_name=model_name,
            defaults={
                'coefficients': model.params.to_dict(),
                'intercept': model.params['const']
            }
        )
