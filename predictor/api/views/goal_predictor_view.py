from django.http import JsonResponse
from predictor.api.services.GoalPredictorService import GoalPredictorService
from django.views.decorators.http import require_http_methods
@require_http_methods(["GET"])
def predict_week_view(request):
    """View to predict the week's matches."""
    predictor = GoalPredictorService()
    
    return JsonResponse(predictor.get_regression_data(), safe=False) 