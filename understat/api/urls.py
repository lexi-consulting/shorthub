from django.urls import path
from .views.mine_league_season_data import mine_league_season_data
from .views.mine_league_data import mine_league_data

urlpatterns = [
    path('mine/', mine_league_season_data, name='mine_league_season_data'),
    path('mine-league-data/', mine_league_data, name='mine_league_data')
] 