from rest_framework.response import Response
from rest_framework.decorators import api_view
from chat.utils import chat_with_openai

@api_view(['GET'])
def test_view(request):
    return Response({'message': 'Hello, World!'})


@api_view(['POST'])
def chat_view(request):
    message = request.data.get('message')
    print(message)
    response = chat_with_openai(message)
    print(response)
    return Response(data=response)
