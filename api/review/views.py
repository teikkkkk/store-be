from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import Review
from .serializers import ReviewSerializer
from api.products.models import Product

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        product_id = self.kwargs.get('pk')
        review_id = self.kwargs.get('review_pk')
        return get_object_or_404(
            Review,
            id=review_id,
            product_id=product_id
        )

    def get_queryset(self):
        product_id = self.kwargs.get('pk')
        return Review.objects.filter(product_id=product_id)

    def perform_create(self, serializer):
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(Product, id=product_id)
        
        # Check if user already reviewed this product
        existing_review = Review.objects.filter(
            user=self.request.user,
            product=product
        ).exists()
        
        if existing_review:
            raise serializer.ValidationError(
                {"detail": "Bạn đã đánh giá sản phẩm này rồi"}
            )
        
        serializer.save(
            user=self.request.user,
            product=product
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"detail": "Bạn không có quyền chỉnh sửa đánh giá này"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not (request.user.is_staff or instance.user == request.user):
            return Response(
                {"detail": "Bạn không có quyền xóa đánh giá này"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def product_reviews(self, request, *args, **kwargs):
        product_id = self.kwargs.get('pk')
        reviews = Review.objects.filter(product_id=product_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def user_reviews(self, request):
        reviews = Review.objects.filter(user=request.user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def edit_review(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.user != request.user:
                return Response(
                    {"detail": "Bạn không có quyền chỉnh sửa đánh giá này"},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['delete'])
    def delete_review(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not (request.user.is_staff or instance.user == request.user):
                return Response(
                    {"detail": "Bạn không có quyền xóa đánh giá này"},
                    status=status.HTTP_403_FORBIDDEN
                )
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )