from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer
from api.cart.models import Cart, CartItem
from rest_framework.decorators import action
import logging
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView


logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @transaction.atomic
    def create(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                return Response(
                    {"error": "Giỏ hàng trống"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            order_number = f"ORD{timezone.now().strftime('%Y%m%d%H%M%S')}"
            total_amount = sum(item.product.price * item.quantity for item in cart.items.all())
            order = Order.objects.create(
                user=request.user,
                order_number=order_number,
                full_name=request.data.get('full_name'),
                phone=request.data.get('phone'),
                email=request.data.get('email'),
                address=request.data.get('address'),
                city=request.data.get('city'),
                total_amount=total_amount,
                payment_method=request.data.get('payment_method', 'cod'),
                order_note=request.data.get('order_note', '')
            )
            order_items = []
            for cart_item in cart.items.all():
                order_items.append(OrderItem(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                ))
            OrderItem.objects.bulk_create(order_items)
            cart.items.all().delete()

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Cart.DoesNotExist:
            return Response(
                {"error": "Không tìm thấy giỏ hàng"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}", exc_info=True)
            return Response(
                {"error": "Lỗi khi tạo đơn hàng"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        try:
            order = self.get_object()
            
            if order.status not in ['pending', 'confirmed']:
                return Response(
                    {"error": "Chỉ có thể hủy đơn hàng ở trạng thái chờ xác nhận hoặc đã xác nhận"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            order.status = 'cancelled'
            order.save()

            serializer = self.get_serializer(order)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def confirm(self, request, pk=None):
        try:
            order = self.get_object()
            if order.status != 'pending':
                return Response(
                    {"error": "Chỉ có thể xác nhận đơn hàng ở trạng thái chờ xác nhận"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.status = 'confirmed'
            order.save()
            
            serializer = self.get_serializer(order)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": f"Không thể xác nhận đơn hàng: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class PaymentCallbackView(APIView):
    @transaction.atomic
    def get(self, request):
        try:
            vnp_ResponseCode = request.GET.get('vnp_ResponseCode')
            vnp_TxnRef = request.GET.get('vnp_TxnRef')   
            vnp_Amount = request.GET.get('vnp_Amount')
            vnp_PayDate = request.GET.get('vnp_PayDate')
            vnp_TransactionStatus = request.GET.get('vnp_TransactionStatus')
            vnp_BankCode = request.GET.get('vnp_BankCode')
            vnp_BankTranNo = request.GET.get('vnp_BankTranNo')
            vnp_CardType = request.GET.get('vnp_CardType')
            vnp_TransactionNo = request.GET.get('vnp_TransactionNo')
            vnp_SecureHash = request.GET.get('vnp_SecureHash')
            
            logger.info(f"VNPay callback received: {request.GET}")
            raw_response = {
                'vnp_ResponseCode': vnp_ResponseCode,
                'vnp_TxnRef': vnp_TxnRef,
                'vnp_Amount': vnp_Amount,
                'vnp_PayDate': vnp_PayDate,
                'vnp_TransactionStatus': vnp_TransactionStatus,
                'vnp_BankCode': vnp_BankCode,
                'vnp_BankTranNo': vnp_BankTranNo,
                'vnp_CardType': vnp_CardType,
                'vnp_TransactionNo': vnp_TransactionNo,
                'vnp_SecureHash': vnp_SecureHash
            }

            try:
                order = Order.objects.get(order_number=vnp_TxnRef)
                logger.info(f"Found order: {order.order_number}")
            except Order.DoesNotExist:
                logger.error(f"Order not found with order_number: {vnp_TxnRef}")
                return Response({
                    "status": "error",
                    "message": "Không tìm thấy đơn hàng"
                }, status=status.HTTP_404_NOT_FOUND)
            if vnp_ResponseCode == "00" and vnp_TransactionStatus == "00":   
                try:
                    order.payment_status = "completed"
                    order.status = "confirmed"
                    order.save()
                    logger.info(f"Order {order.order_number} updated to completed")

                    Payment.objects.create(
                        order=order,
                        payment_id=vnp_TransactionNo,
                        amount=int(vnp_Amount) / 100,
                        status="completed",
                        created_at=timezone.now(),
                        raw_response=raw_response
                    )
                    logger.info(f"Payment record created for order {order.order_number}")
                    try:
                        cart = Cart.objects.get(user=order.user)
                        cart.items.all().delete()
                        logger.info(f"Cart cleared for user {order.user.id}")
                    except Cart.DoesNotExist:
                        logger.warning(f"No cart found for user {order.user.id}")
                    
                    return Response({
                        "status": "success",
                        "message": "Thanh toán thành công",
                        "order_number": order.order_number
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    logger.error(f"Error processing successful payment: {str(e)}")
                    return Response({
                        "status": "error",
                        "message": "Lỗi khi xử lý thanh toán thành công"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                try:
                    Payment.objects.create(
                        order=order,
                        payment_id=vnp_TransactionNo,
                        amount=int(vnp_Amount) / 100,
                        status="failed",
                        created_at=timezone.now(),
                        raw_response=raw_response
                    )
                    logger.info(f"Failed payment record created for order {order.order_number}")
                    
                    order.payment_status = "failed"
                    order.save()
                    logger.info(f"Order {order.order_number} updated to failed")
                    
                    return Response({
                        "status": "failed", 
                        "message": "Thanh toán thất bại",
                        "order_number": order.order_number
                    }, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    logger.error(f"Error processing failed payment: {str(e)}")
                    return Response({
                        "status": "error",
                        "message": "Lỗi khi xử lý thanh toán thất bại"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Payment callback error: {str(e)}", exc_info=True)
            return Response({
                "status": "error",
                "message": "Lỗi xử lý thanh toán"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)