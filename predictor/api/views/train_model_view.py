from django.http import JsonResponse, HttpRequest
from predictor.api.services.GoalPredictorService import GoalPredictorService
from predictor.api.models.TrainedModel import TrainedModel
from typing import Dict
import logging
import numpy as np
import pickle

logger = logging.getLogger(__name__)

def train_model_view(request: HttpRequest) -> JsonResponse:
    """Train a CNN model and save it to the database.
    
    Args:
        request: The HTTP request object.
        
    Returns:
        JsonResponse containing training metrics including accuracy, GPU count,
        and sample sizes.
        
    Raises:
        JsonResponse: With error details if training or saving fails.
    """
    try:
        model_trainer = GoalPredictorService()
        result = model_trainer.train_and_test_cnn()
        
        # Serialize the weights to bytes
        weights_bytes = pickle.dumps(model_trainer.model.get_weights())
        
        trained_model = TrainedModel(
            model_name="cnn_model",
            architecture=model_trainer.model.to_json(),
            weights=weights_bytes
        )
        trained_model.save()
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        return JsonResponse(
            {"error": "Model training failed", "details": str(e)}, 
            status=500
        )

