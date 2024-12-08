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

    def get_html(self) -> str:
        """Return an HTML representation of the match.
        
        Returns:
            str: HTML string with match details formatted as a card
        """
        result_class = "text-gray-600" if not self.is_result else (
            "text-green-600" if self.home_goals > self.away_goals else 
            "text-red-600" if self.home_goals < self.away_goals else 
            "text-yellow-600"
        )
        
        return f"""
        <div class="border rounded-lg p-4 mb-4 shadow-sm">
            <div class="flex justify-between items-center">
                <div class="text-lg font-semibold">{self.home_team}</div>
                <div class="text-xl {result_class}">{self.home_goals} - {self.away_goals}</div>
                <div class="text-lg font-semibold">{self.away_team}</div>
            </div>
            <div class="text-sm text-gray-500 mt-2">
                <div>xG: {self.home_xg:.2f} - {self.away_xg:.2f}</div>
                <div>Date: {self.datetime.strftime('%Y-%m-%d %H:%M')}</div>
            </div>
            {self._get_forecast_html() if not self.is_result else ''}
        </div>
        """

    def _get_forecast_html(self) -> str:
        """Return HTML for match forecast.
        
        Returns:
            str: HTML string with forecast probabilities
        """
        return f"""
        <div class="text-sm text-gray-600 mt-2">
            <div>Forecast: W: {self.forecast_win:.0%} D: {self.forecast_draw:.0%} L: {self.forecast_loss:.0%}</div>
        </div>
        """