from django.db.models.signals import post_save
from django.dispatch import receiver
from understat.api.models.HTMLRequest import HTMLRequest
from understat.api.models.Team import Team
from understat.api.models.Match import Match
import json
from django.utils import timezone

class UnderstatDatabaseService:
    """Service for updating database models based on HTMLRequest signals."""

    @staticmethod
    @receiver(post_save, sender=HTMLRequest)
    def update_team_and_match_data(sender, instance, created, **kwargs):
        """Log Team and Match data when a new HTMLRequest is created."""
        if created:
            try:
                # Clean up the string to make it valid JSON
                cleaned_data = (
                    instance.parsed_data
                    .replace("True", "true")
                    .replace("False", "false")
                    .replace("\'", '"')
                    .replace("None", "0")
                )
                parsed_data = json.loads(cleaned_data)
                dates_data = parsed_data.get('datesData', [])
                
                for match_data in dates_data:
                    # Update or create home team
                    home_team_data = match_data['h']
                    home_team, _ = Team.objects.update_or_create(
                        team_id=home_team_data['id'],
                        defaults={
                            'title': home_team_data['title'],
                            'short_title': home_team_data['short_title']
                        }
                    )
                    
                    # Update or create away team
                    away_team_data = match_data['a']
                    away_team, _ = Team.objects.update_or_create(
                        team_id=away_team_data['id'],
                        defaults={
                            'title': away_team_data['title'],
                            'short_title': away_team_data['short_title']
                        }
                    )
                    
                    # Convert naive datetime to timezone-aware
                    match_datetime = timezone.make_aware(
                        timezone.datetime.strptime(match_data['datetime'], '%Y-%m-%d %H:%M:%S')
                    )

                    if 'forecast' not in match_data:
                        match_data['forecast'] = {"w": 0, "l": 0, "d": 0}
                    
                    Match.objects.update_or_create(
                        match_id=match_data['id'],
                        defaults={
                            'is_result': match_data['isResult'],
                            'home_team': home_team,
                            'away_team': away_team,
                            'home_goals': int(match_data['goals']['h']),
                            'away_goals': int(match_data['goals']['a']),
                            'home_xg': float(match_data['xG']['h']),
                            'away_xg': float(match_data['xG']['a']),
                            'datetime': match_datetime,
                            'forecast_win': float(match_data['forecast']['w']),
                            'forecast_draw': float(match_data['forecast']['d']),
                            'forecast_loss': float(match_data['forecast']['l']),
                        }
                    )
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"Error updating database: {e}")