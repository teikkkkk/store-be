from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from api.products.models import Product
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response(
                {"message": "Giỏ hàng trống"},
                status=status.HTTP_404_NOT_FOUND
            )

    @transaction.atomic
    def post(self, request):
        try:
            product_id = request.data.get('product_id')
            quantity = int(request.data.get('quantity', 1))

            logger.info(f"Adding product {product_id} with quantity {quantity} to cart")

            if not product_id:
                return Response(
                    {"error": "Thiếu product_id"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if quantity <= 0:
                return Response(
                    {"error": "Số lượng phải lớn hơn 0"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            product = Product.objects.get(id=product_id)
            
            cart, created = Cart.objects.get_or_create(user=request.user)
            logger.info(f"Cart {'created' if created else 'retrieved'} for user {request.user.id}")
            
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not item_created:
                cart_item.quantity = quantity
                cart_item.save()
                logger.info(f"Updated quantity for product {product_id} to {cart_item.quantity}")

            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Product.DoesNotExist:
            logger.error(f"Product {product_id} not found")
            return Response(
                {"error": "Sản phẩm không tồn tại"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            logger.error(f"Invalid quantity value: {e}")
            return Response(
                {"error": "Số lượng không hợp lệ"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error adding to cart: {str(e)}", exc_info=True)
            return Response(
                {"error": "Lỗi khi thêm sản phẩm vào giỏ hàng"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            serializer = CartItemSerializer(cart.items.all(), many=True)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response(
                {"message": "Giỏ hàng trống"},
                status=status.HTTP_404_NOT_FOUND
            )

    @transaction.atomic
    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
            
            cart = Cart.objects.get(user=request.user)
            serializer = CartSerializer(cart)
            return Response(serializer.data)
            
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Sản phẩm không có trong giỏ hàng"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting cart item: {str(e)}", exc_info=True)
            return Response(
                {"error": "Lỗi khi xóa sản phẩm khỏi giỏ hàng"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )