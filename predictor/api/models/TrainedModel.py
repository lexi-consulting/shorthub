from django.db import models

class TrainedModel(models.Model):
    """Model representing a trained logistic regression model."""
    model_name = models.CharField(max_length=50)
    coefficients = models.JSONField()
    intercept = models.FloatField()

    def __str__(self) -> str:
        """Return the string representation of the trained model."""
        return f"TrainedModel: {self.model_name}" 