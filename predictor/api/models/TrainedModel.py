from django.db import models

class TrainedModel(models.Model):
    """Model representing a trained CNN model."""
    model_name = models.CharField(max_length=50)
    architecture = models.JSONField()  # Store the model architecture
    weights = models.BinaryField(null=True, blank=True)  # Store the model weights, nullable

    def __str__(self) -> str:
        """Return the string representation of the trained model."""
        return f"TrainedModel: {self.model_name}" 