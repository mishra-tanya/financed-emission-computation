from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers.user_serializers import UserRegistrationSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view

# registration auth_user table + finance_profile table
@api_view(['GET']) 
def testing(request):
    return Response({"message": "Yay success!"})

class Register(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# login and setting token 
class Login(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# blacklisting refresh token
class Logout(APIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  
                return Response({"detail": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
            else:
                return Response({"detail": "No refresh token provided"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
