from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .serializers import SignupSerializer, LoginSerializer, UserSerializer
from .models import User
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import UserRateThrottle

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import LoginSerializer

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        # Create tokens for the user
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.pk,
            "email": user.email
        })

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from .models import FriendRequest, Friendship  # Make sure this line is present
from .serializers import UserSerializer, FriendRequestSerializer, FriendshipSerializer


from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from .models import User
from .serializers import UserSerializer

class SearchUserView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination  # For pagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip().lower()
        if '@' in query:
            # Exact match for email
            return User.objects.filter(email__iexact=query)
        else:
            # Partial match for name
            return User.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([UserRateThrottle])
def send_friend_request(request):
    to_user_id = request.data.get('to_user_id')
    if to_user_id == request.user.id:
        return Response({"detail": "You cannot send a friend request to yourself."}, status=status.HTTP_400_BAD_REQUEST)

    to_user = User.objects.get(id=to_user_id)
    if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        return Response({"detail": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)

    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    return Response({"detail": "Friend request sent."}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def manage_friend_request(request, pk, action):
    try:
        friend_request = FriendRequest.objects.get(pk=pk, to_user=request.user)
    except FriendRequest.DoesNotExist:
        return Response({"detail": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)

    if action == 'accept':
        friend_request.accept()
        return Response({"detail": "Friend request accepted."})
    elif action == 'reject':
        friend_request.reject()
        return Response({"detail": "Friend request rejected."})
    return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

from .serializers import FriendshipSerializer,FriendRequestSerializer

class ListFriendsView(generics.ListAPIView):
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Friendship.objects.filter(Q(from_user=self.request.user) | Q(to_user=self.request.user))
        print("Queryset:", queryset)
        return queryset


class ListPendingRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, status='pending')
