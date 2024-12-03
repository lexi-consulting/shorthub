from django.db import models
from understat.api.models.Team import Team

class Match(models.Model):
    """Model representing a match."""
    match_id = models.IntegerField()
    is_result = models.BooleanField()
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    home_goals = models.IntegerField()
    away_goals = models.IntegerField()
    home_xg = models.FloatField()
    away_xg = models.FloatField()
    datetime = models.DateTimeField()
    forecast_win = models.FloatField()
    forecast_draw = models.FloatField()
    forecast_loss = models.FloatField()

    def __str__(self) -> str:
        """Return the string representation of the match."""
        return f"{self.home_team} vs {self.away_team} on {self.datetime}"