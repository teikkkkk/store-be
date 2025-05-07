# api/products/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count, Sum
from .models import Product
from .serializers import ProductSerializer
from api.orders.models import OrderItem

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def get_permissions(self):
        if self.request.method == "GET":   
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]   

    def get_queryset(self):
        queryset = Product.objects.all() 
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |   
                Q(description__icontains=search)   
            ) 
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category) 
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price) 
        is_top = self.request.query_params.get('is_top', None)
        if is_top == 'true':
            queryset = queryset.filter(is_top=True) 
        sort_by = self.request.query_params.get('sort', None)
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'sales':
            queryset = Product.objects.annotate(
                total_sold=Sum('orderitem__quantity')
            ).order_by('-total_sold')
        
        limit = self.request.query_params.get('limit', None)
        if limit:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError:
                pass
                
        return queryset

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
  
    def get_permissions(self):
        if self.request.method == "GET":   
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]  

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TopProductView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Product.objects.filter(
            orderitem__isnull=False
        ).annotate(
            total_sold=Sum('orderitem__quantity')
        ).order_by('-total_sold')[:10]