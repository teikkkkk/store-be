from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import RoomChat
from .serializers import RoomChatSerializer
from firebase_config import firebase_auth, firebase_db  # Import initialized Firebase objects
import uuid
import logging

logger = logging.getLogger(__name__)

class CreateRoomChat(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        existing_room = RoomChat.objects.filter(user=user).first()
        
        if existing_room:
            try:
                logger.info(f"User {user.id} already has a chat room: {existing_room.room_id}")
                custom_token = firebase_auth.create_custom_token(str(user.id)).decode('utf-8')
                
                return Response({
                    "room_id": existing_room.room_id,
                    "firebase_token": custom_token,
                    "is_existing": True
                })
            except Exception as e:
                logger.error(f"Error generating token for existing room: {e}")
                return Response({"error": str(e)}, status=500)
        room_id = str(uuid.uuid4())
        room_chat = RoomChat.objects.create(user=user, room_id=room_id)

        try:
            logger.info(f"Creating new chat room for user ID: {user.id}")
            custom_token = firebase_auth.create_custom_token(str(user.id)).decode('utf-8')
            logger.info(f"Generated custom token length: {len(custom_token)}")

            chat_room_ref = firebase_db.reference(f"chat_rooms/{room_id}")
            chat_room_ref.set({
                "initiator": str(user.id),
                "created_at": room_chat.created_at.isoformat()
            })
            logger.info(f"Created chat room in Firebase RTDB: {room_id}")

            return Response({
                "room_id": room_id,
                "firebase_token": custom_token,
                "is_existing": False
            })
        except Exception as e:
            logger.error(f"Error creating chat room or generating token: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
            return Response({"error": str(e)}, status=500)

class GetRoomChats(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        room_chat = RoomChat.objects.filter(user=user).first()
        if room_chat:
            serializer = RoomChatSerializer(room_chat)
            return Response(serializer.data)
        return Response({"message": "No chat room found"}, status=404)

class AdminRoomChats(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        room_chats = RoomChat.objects.all().order_by('-created_at')
        serializer = RoomChatSerializer(room_chats, many=True)
        return Response(serializer.data)

class GetFirebaseToken(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            custom_token = firebase_auth.create_custom_token(str(user.id)).decode('utf-8')
            return Response({"token": custom_token})
        except Exception as e:
            logger.error(f"Error generating Firebase token: {str(e)}")
            return Response({"error": str(e)}, status=500)