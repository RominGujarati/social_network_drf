from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, UserSearchView, FriendRequestViewSet

router = DefaultRouter()
router.register(r'friend-requests', FriendRequestViewSet, basename='friend-request')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('users/search/', UserSearchView.as_view(), name='user-search'),
    path('', include(router.urls)),
]
