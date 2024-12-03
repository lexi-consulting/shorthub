from django.db.models.signals import post_save
from django.dispatch import receiver
from understat.api.models.HTMLRequest import HTMLRequest
from understat.api.models.Team import Team
from understat.api.models.Match import Match

class UnderstatDatabaseService:
    """Service for updating database models based on HTMLRequest signals."""

    @staticmethod
    @receiver(post_save, sender=HTMLRequest)
    def update_team_and_match_data(sender, instance, created, **kwargs):
        """Log Team and Match data when a new HTMLRequest is created."""
        if created:
            print(f"HTMLRequest created: {instance.url}")