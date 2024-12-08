from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from understat.api.services.UnderstatService import UnderstatService
from understat.api.constants.UnderstatConstants import UnderstatConstants
from typing import Any

@require_http_methods(["POST"])
def mine_league_data(request: Any) -> HttpResponse:
    """API endpoint to mine league data, defaulting to the latest season if not specified."""
    leagues = request.POST.getlist('league')
    season = max(UnderstatConstants.SEASONS)

    if not leagues:
        error_message = render_to_string('shared/components/forms/message.html', {
            'id': 'message',
            'results': ['Missing league parameter'],
            'is_error': True
        })
        return HttpResponse(error_message, status=400)

    results = {}
    messages = []
    for league in leagues:
        results[league] = []
        data, error = UnderstatService.mine_league_season_data(league, season)
        if error:
            error_message = render_to_string('shared/components/forms/message.html', {
                'id': 'message',
                'results': [error],
                'is_error': True
            })
            return HttpResponse(error_message, status=400)
        results[league].append(season)
        messages.append(f'Data for {league} {season} fetched successfully')
    
    success_message = render_to_string('shared/components/forms/message.html', {
        'id': 'message',
        'results': messages,
        'is_error': False
    })
    return HttpResponse(success_message) 