from django.db import models
from django.utils import timezone

class UnderstatHTMLRequest(models.Model):
    """
    Model to store HTML requests made to Understat, including the URL, 
    response content, parsed data, and timestamps for creation and modification.
    """
    url: str = models.URLField(max_length=200)
    response: str = models.TextField()
    parsed_data: str = models.TextField()  # Changed from JSONField to TextField
    success: bool = models.BooleanField(default=True)
    date_created: timezone.datetime = models.DateTimeField(auto_now_add=True)
    date_modified: timezone.datetime = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Returns a string representation of the model instance.
        """
        return f"UnderstatHTMLRequest(url={self.url})"
