from django.db import models

class Team(models.Model):
    """Model representing a team in a match."""
    team_id = models.IntegerField()
    title = models.CharField(max_length=100)
    short_title = models.CharField(max_length=3)

    def __str__(self) -> str:
        """Return the string representation of the team."""
        return self.title