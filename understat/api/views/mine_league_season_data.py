from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from understat.api.services.UnderstatService import UnderstatService

@require_http_methods(["POST"])
def mine_league_season_data(request):
    """Handle mining of league season data from POST request body."""
    league = request.POST.get('league')
    if not league:
        return JsonResponse({'error': 'Missing league parameter'}, status=400)
    
    season = request.POST.get('season')
    if not season:
        return JsonResponse({'error': 'Missing season parameter'}, status=400)
    
    result, error = UnderstatService.mine_league_season_data(league, season)
    if error:
        return JsonResponse({'error': error}, status=400)
    return JsonResponse({'success': result}, safe=False)