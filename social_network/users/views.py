from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import Q
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import FriendRequest
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email__iexact=serializer.data["email"]).first()

        if user and user.check_password(serializer.data["password"]):
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            )
        return Response({"detail": "Invalid credentials"}, status=400)


class UserSearchPagination(PageNumberPagination):
    page_size = 10  # We can override the default page size here if needed
    page_size_query_param = "page_size"
    max_page_size = 100


class UserSearchView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserSearchPagination

    def get_queryset(self):
        query = self.request.query_params.get("q", "").lower()
        if "@" in query:
            return User.objects.filter(email__iexact=query)
        return User.objects.filter(username__icontains=query)


class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        sender = request.user
        receiver = User.objects.get(id=request.data["receiver_id"])

        if not receiver.id:
            return Response(
                {"detail": "Receiver ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if sender.id == receiver.id:
            return Response(
                {"detail": "You cannot send a friend request to yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recent_requests = FriendRequest.objects.filter(
            sender=sender, created_at__gte=now() - timedelta(minutes=1)
        )

        if recent_requests.count() >= 3:
            return Response(
                {"detail": "You can't send more than 3 requests in a minute."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        friend_request, created = FriendRequest.objects.get_or_create(
            sender=sender, receiver=receiver
        )
        if not created:
            if friend_request.status == "P":
                return Response(
                    {"detail": "Friend request already sent and pending."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif friend_request.status == "A":
                return Response(
                    {"detail": "You are already friends."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"detail": "Friend request sent."}, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user != instance.receiver:
            return Response(
                {
                    "detail": "You do not have permission to accept or reject this friend request."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        status_map = {"A": "Accepted", "R": "Rejected", "P": "Pending"}
        new_status = request.data.get("status")
        if new_status not in ["A", "R"]:
            return Response(
                {"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST
            )
        instance.status = new_status
        instance.save()
        return Response({"detail": f"Friend request {status_map[new_status]}."})

    def list(self, request, *args, **kwargs):
        status_filter = request.query_params.get("status", "A")
        if status_filter == "P":
            queryset = FriendRequest.objects.filter(receiver=request.user, status="P")
        elif status_filter == "A":
            queryset = FriendRequest.objects.filter(
                Q(sender=request.user) | Q(receiver=request.user), status="A"
            )
        elif status_filter == "R":
            queryset = FriendRequest.objects.filter(
                Q(sender=request.user) | Q(receiver=request.user), status="R"
            )
        else:
            return Response(
                {
                    "detail": "Invalid status filter. Use 'P' for pending, 'A' for accepted, or 'R' for rejected."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = [
            {
                "id": req.id,
                "sender": req.sender.username,
                "receiver": req.receiver.username,
                "status": req.status,
            }
            for req in queryset
        ]

        return Response(response_data)
