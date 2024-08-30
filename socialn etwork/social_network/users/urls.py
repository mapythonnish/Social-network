from django.urls import path
from .views import SignupView, LoginAPIView, SearchUserView, send_friend_request, manage_friend_request, ListFriendsView, ListPendingRequestsView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('search/', SearchUserView.as_view(), name='search_users'),
    path('friends/send/', send_friend_request, name='send_friend_request'),
    path('friends/manage/<int:pk>/<str:action>/', manage_friend_request, name='manage_friend_request'),
    path('friends/', ListFriendsView.as_view(), name='list_friends'),
    path('friends/pending/',ListPendingRequestsView.as_view(), name='list_pending_requests'),
]
