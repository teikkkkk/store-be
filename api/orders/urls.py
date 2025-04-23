from django.urls import path, include
from .views import OrderViewSet,PaymentCallbackView

 
urlpatterns = [
    path('', OrderViewSet.as_view({'get': 'list', 'post': 'create'}), name='order-list'),
    path('<int:pk>/', OrderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='order-detail'),
    path('<int:pk>/cancel/', OrderViewSet.as_view({'post': 'cancel'}), name='order-cancel'),
    path('<int:pk>/confirm/', OrderViewSet.as_view({'post': 'confirm'}), name='order-confirm'),
    path('payment/vnpay-return/', PaymentCallbackView.as_view(), name='vnpay-return'),
]
