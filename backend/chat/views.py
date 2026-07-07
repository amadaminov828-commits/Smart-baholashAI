from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .services import ChatService
import logging

logger = logging.getLogger(__name__)

class ChatView(APIView):
    # Depending on requirements, we can restrict to authenticated users
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        # Handle both JSON and FormData
        message = request.data.get('message')
        history_raw = request.data.get('history', [])
        
        # If history is a string (coming from FormData), parse it
        import json
        if isinstance(history_raw, str):
            try:
                history = json.loads(history_raw)
            except:
                history = []
        else:
            history = history_raw

        image_file = request.FILES.get('image')
        
        if not message and not image_file:
            return Response({"error": "Xabar yoki rasm bo'sh bo'lishi mumkin emas"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            chat_service = ChatService()
            
            image_data = None
            image_mime_type = None
            if image_file:
                image_data = image_file.read()
                image_mime_type = image_file.content_type

            response_text = chat_service.get_chat_response(
                message or "Ushbu rasmni tahlil qiling", 
                history=history,
                image_data=image_data,
                image_mime_type=image_mime_type
            )
            return Response({"response": response_text}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"ChatView error: {str(e)}")
            return Response({"error": f"Serverda xatolik yuz berdi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
