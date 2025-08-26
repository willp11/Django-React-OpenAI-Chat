from rest_framework.response import Response
from rest_framework.decorators import api_view
from chat.utils import chat_with_openai_stream
from rest_framework import status
from django.http import StreamingHttpResponse
from api.models import Chat, ChatMessage
import json

@api_view(['POST'])
def create_chat(request):
    chat = Chat.objects.create()
    return Response(data={'chat_id': chat.id})


@api_view(['GET'])
def get_chat_messages(request, chat_id):
    chat = Chat.objects.get(id=chat_id)
    messages = ChatMessage.objects.filter(chat=chat)
    return Response(data=[{'message': message.message, 'content': message.content} for message in messages])


@api_view(['POST'])
def chat_stream(request, chat_id):
    """Streaming chat endpoint using Server-Sent Events"""
    message_text = request.data.get('message')
    chat = Chat.objects.get(id=chat_id)
    chat_message = ChatMessage.objects.create(chat=chat, content='', message=message_text)

    if not message_text:
        return Response(
            {'error': 'Message is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def event_stream():
        content_parts = []
        try:
            for chunk in chat_with_openai_stream(message_text):
                if chunk['type'] == 'content':
                    content_parts.append(chunk['content'])
                yield f"data: {json.dumps(chunk)}\n\n"
            
            full_content = ''.join(content_parts)
            chat_message.content = full_content
            chat_message.save()
            
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
