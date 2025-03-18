from django.urls import path
from .views import RegisterView ,UserInfoView 
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
]