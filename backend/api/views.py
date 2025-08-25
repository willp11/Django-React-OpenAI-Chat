from rest_framework.response import Response
from rest_framework.decorators import api_view
from chat.utils import chat_with_openai, chat_with_openai_stream
from rest_framework import status
from django.http import StreamingHttpResponse
import json

@api_view(['GET'])
def test_view(request):
    return Response({'message': 'Hello, World!'})


@api_view(['POST'])
def chat_view(request):
    message = request.data.get('message')
    response = chat_with_openai(message)
    if response['success']:
        return Response(data={'reply': response['reply']})
    else:
        return Response(data={'error': response['error']}, status=500)


@api_view(['POST'])
def chat_stream_view(request):
    """Streaming chat endpoint using Server-Sent Events"""
    message = request.data.get('message')
    
    if not message:
        return Response(
            {'error': 'Message is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def event_stream():
        try:
            for chunk in chat_with_openai_stream(message):
                if chunk['type'] == 'content':
                    yield f"data: {json.dumps(chunk)}\n\n"
                elif chunk['type'] == 'done':
                    yield f"data: {json.dumps(chunk)}\n\n"
                elif chunk['type'] == 'error':
                    yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            error_chunk = {'type': 'error', 'error': str(e)}
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
