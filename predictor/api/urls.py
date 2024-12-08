from django.urls import path
from predictor.api.views.goal_predictor_view import predict_week_view

urlpatterns = [
    path('api/predict-week/', predict_week_view, name='predict_week'),
]
