from chat.client import create_openai_client
from chat.chroma import create_rag_prompt
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def chat_with_openai_stream(message, model=None, max_tokens=1000):
    """
    Stream a response from OpenAI's chat API
    
    Args:
        message (str): The user's message
        model (str): The OpenAI model to use (defaults to settings.OPENAI_MODEL)
        max_tokens (int): Maximum tokens for the response
    
    Yields:
        dict: Streaming response chunks
    """
    try:
        client = create_openai_client()
        model = model or settings.OPENAI_MODEL
        prompt = create_rag_prompt(message)
        
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
            stream=True  # Enable streaming
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield {
                    'type': 'content',
                    'content': chunk.choices[0].delta.content,
                    'model': model
                }

        yield {
            'type': 'done',
            'model': model
        }
        
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        yield {
            'type': 'error',
            'error': str(e)
        }
