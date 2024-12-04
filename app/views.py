from django.shortcuts import render
from understat.api.constants.UnderstatConstants import UnderstatConstants

def index_view(request):
    return render(request, 'base/index.html')

def home_view(request):
    return render(request, 'base/home.html')

def league_season_form(request):
    """Render the form for selecting league and season."""
    context = {
        'leagues': UnderstatConstants.LEAGUES,
        'seasons': UnderstatConstants.SEASONS
    }
    return render(request, 'understat/league_season_form.html', context)  