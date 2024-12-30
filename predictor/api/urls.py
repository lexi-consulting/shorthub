from django.urls import path
from predictor.api.views.goal_predictor_view import predict_week_view, predict_fixtures_view
from predictor.api.views.train_model import train_model_view   

urlpatterns = [
    path('api/predict-week/', predict_week_view, name='predict_week'),
    path('api/train-model/', train_model_view, name='train_model'),
    path('api/predict-fixtures/', predict_fixtures_view, name='predict_fixtures'),
]
