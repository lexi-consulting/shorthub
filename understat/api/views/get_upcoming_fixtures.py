from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from understat.api.models.Match import Match

def get_upcoming_fixtures(request) -> JsonResponse:
    """Get upcoming fixtures within the next week and return as JSON."""
    print('Fetching upcoming fixtures...')
    now = timezone.now()
    next_week = now + timedelta(weeks=1)
    
    upcoming_matches = list(Match.objects.filter(
        is_result=0,
        datetime__range=(now, next_week)
    ).select_related('home_team', 'away_team')
    .order_by('datetime'))
    
    matches_data = [{
        'datetime': match.datetime.strftime('%Y-%m-%d %H:%M'),
        'home_team': match.home_team.title,
        'away_team': match.away_team.title,
    } for match in upcoming_matches]
    
    return JsonResponse({'matches': matches_data}) 