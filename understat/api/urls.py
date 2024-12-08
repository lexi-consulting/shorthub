from django.urls import path
from .views.mine_league_season_data import mine_league_season_data
from .views.mine_league_data import mine_league_data
from .views.get_upcoming_fixtures import get_upcoming_fixtures

urlpatterns = [
    path('mine/', mine_league_season_data, name='mine_league_season_data'),
    path('mine-league-data/', mine_league_data, name='mine_league_data'),
    path('upcoming-fixtures/', get_upcoming_fixtures, name='get_upcoming_fixtures'),
] 