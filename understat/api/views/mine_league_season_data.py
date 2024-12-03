from django.http import JsonResponse
from understat.api.services.UnderstatService import UnderstatService

def mine_league_season_data(request):
    """Handle mining of league season data with optional query parameters."""
    league = request.GET.get('league')
    if not league:
        return JsonResponse({'error': 'Missing league parameter'}, status=400)
    
    season = request.GET.get('season')
    if not season:
        return JsonResponse({'error': 'Missing season parameter'}, status=400)
    
    result, error = UnderstatService.mine_league_season_data(league, season)
    if error:
        return JsonResponse({'error': error}, status=400)
    return JsonResponse({'success': result}, safe=False)