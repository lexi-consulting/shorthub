from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from understat.api.models.Match import Match

def get_upcoming_fixtures(request) -> JsonResponse:
    """Get upcoming fixtures within a specified date range and return as JSON."""
    print('Fetching upcoming fixtures...')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    model_name = request.GET.get('model')

    if not start_date_str or not end_date_str:
        now = timezone.now()
        next_week = now + timedelta(weeks=1)
        start_date = now
        end_date = next_week
    else:
        start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d')

    upcoming_matches = list(Match.objects.filter(
        is_result=0,
        datetime__range=(start_date, end_date)
    ).select_related('home_team', 'away_team')
    .order_by('datetime'))

    matches_data = [{
        'datetime': match.datetime.strftime('%Y-%m-%d %H:%M'),
        'home_team': match.home_team.title,
        'away_team': match.away_team.title,
    } for match in upcoming_matches]

    return JsonResponse({'matches': matches_data, 'model': model_name}) 