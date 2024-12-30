from django.http import JsonResponse
from predictor.api.services.GoalPredictorService import GoalPredictorService
from django.views.decorators.http import require_http_methods
@require_http_methods(["GET"])
def predict_week_view(request):
    """View to predict the week's matches."""
    predictor = GoalPredictorService()
    
    return JsonResponse(predictor.get_regression_data(), safe=False) 

@require_http_methods(["GET"])
def predict_fixtures_view(request):
    """View to predict fixtures based on selected date range and model."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    model_name = request.GET.get('model')

    # Use the GoalPredictorService with the selected model
    predictor = GoalPredictorService(model_name=model_name)
    prediction_results = predictor.predict_fixtures(start_date, end_date)

    return JsonResponse({'predictions': prediction_results}) 