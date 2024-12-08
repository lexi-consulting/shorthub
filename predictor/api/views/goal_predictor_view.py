from django.http import JsonResponse
from predictor.api.services.GoalPredictorService import GoalPredictorService

def predict_week_view(request):
    """View to predict the week's matches."""
    predictor = GoalPredictorService()
    
    return JsonResponse(predictor.get_regression_data(), safe=False) 