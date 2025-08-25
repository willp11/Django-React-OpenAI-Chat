from chat.client import create_openai_client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def chat_with_openai(message, model=None, max_tokens=1000):
    """
    Send a message to OpenAI's chat API and return the response
    
    Args:
        message (str): The user's message
        model (str): The OpenAI model to use (defaults to settings.OPENAI_MODEL)
        max_tokens (int): Maximum tokens for the response
    
    Returns:
        dict: Response containing the AI's reply and metadata
    """
    try:
        client = create_openai_client()
        model = model or settings.OPENAI_MODEL
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": message}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return {
            'success': True,
            'reply': response.choices[0].message.content,
            'model': model,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        }
        
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
