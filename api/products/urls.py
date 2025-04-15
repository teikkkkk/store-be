# api/products/urls.py
from django.urls import path
from .views import ProductListCreateView, ProductDetailView

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('search/', ProductListCreateView.as_view(), name='product-search'),
    path('category/<int:category_id>/', ProductListCreateView.as_view(), name='product-by-category'),
    path('top/', ProductListCreateView.as_view(), {'is_top': 'true'}, name='top-products'),
    
]