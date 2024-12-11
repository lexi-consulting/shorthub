from django.http import JsonResponse
from predictor.api.services.GoalPredictorService import GoalPredictorService

def train_model_view(request):
    """View to train the logistic regression model and save it to the database."""
    model_trainer = GoalPredictorService()
    result = model_trainer.train_and_test_cnn()
    
    return JsonResponse(result, safe=True)

