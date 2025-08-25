from openai import OpenAI
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def create_openai_client():
    """Create and return an OpenAI client instance"""
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    return OpenAI(api_key=api_key)
