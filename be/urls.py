"""
URL configuration for be project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views import RegisterView,UserInfoView
from api.payment.views import CreateVNPayPayment
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/products/', include('api.products.urls')),
    path('api/categories/', include('api.categories.urls')),
    path('api/users/', include('api.users.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   
    path('api/register/', RegisterView.as_view(), name='register'),   
     path('api/user-info/', UserInfoView.as_view(), name='user_info'),
    path('api/chat/', include('api.chat.urls')),
    path('api/cart/', include('api.cart.urls')),
    path('api/payment/create-vnpay-payment/', CreateVNPayPayment.as_view(), name='create-vnpay-payment'),
    path('api/orders/', include('api.orders.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)