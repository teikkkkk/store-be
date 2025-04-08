# api/urls.py
from django.urls import path
from .views import UserListCreateView, UserDetailView, UserProfileView

urlpatterns = [
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]