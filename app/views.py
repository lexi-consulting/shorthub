from django.shortcuts import render
from understat.api.constants.UnderstatConstants import UnderstatConstants

def index_view(request):
    return render(request, 'base/index.html')

def home_view(request):
    return render(request, 'base/home.html')

def league_season_form(request):
    """Render the form for selecting league and season using separate tables with pagination."""
    leagues = [(league,) for league in UnderstatConstants.LEAGUES]
    seasons = [(season,) for season in UnderstatConstants.SEASONS]

    context = {
        'league_headers': ['League', ''],
        'season_headers': ['Season', ''],
        'league_items': leagues,
        'season_items': seasons,
        'form_field_league': 'league',
        'form_field_season': 'season',
        'allow_multiple': True
    }
    return render(request, 'understat/league_season_form.html', context)

def league_form_view(request):
    """Render the form for selecting league using a separate table with pagination."""
    leagues = [(league,) for league in UnderstatConstants.LEAGUES]

    context = {
        'league_headers': ['League', ''],
        'league_items': leagues,
        'form_field_league': 'league',
        'allow_multiple': True
    }
    return render(request, 'understat/league_form.html', context)  