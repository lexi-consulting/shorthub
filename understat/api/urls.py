from django.urls import path
from .views.mine_league_season_data import mine_league_season_data

urlpatterns = [
    path('mine/', mine_league_season_data, name='mine_league_season_data')
] 