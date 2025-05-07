# api/products/urls.py
from django.urls import path
from .views import ProductListCreateView, ProductDetailView, TopProductView
from api.review.views import ReviewViewSet

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('search/', ProductListCreateView.as_view(), name='product-search'),
    path('category/<int:category_id>/', ProductListCreateView.as_view(), name='product-by-category'),
    path('top-selling/', TopProductView.as_view(), name='top-selling-products'),
    path('<int:pk>/reviews/', ReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-reviews'),
    path('<int:pk>/reviews/<int:review_pk>/edit/', ReviewViewSet.as_view({'put': 'edit_review'}), name='edit-review'),
    path('<int:pk>/reviews/<int:review_pk>/delete/', ReviewViewSet.as_view({'delete': 'delete_review'}), name='delete-review'),
]