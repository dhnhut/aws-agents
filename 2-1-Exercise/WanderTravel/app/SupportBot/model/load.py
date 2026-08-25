from strands.models.bedrock import BedrockModel


MODEL_ID = "us.amazon.nova-2-lite-v1:0"

def load_model() -> BedrockModel:
    """Get Bedrock model client using IAM credentials."""
    return BedrockModel(model_id=MODEL_ID)
