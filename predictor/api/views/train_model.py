from django.http import JsonResponse
from predictor.api.services.ModelTrainingService import ModelTrainingService

def train_model_view(request):
    """View to train the logistic regression model and save it to the database."""
    model_trainer = ModelTrainingService()
    result = model_trainer.train_model()
    
    return JsonResponse(result)
