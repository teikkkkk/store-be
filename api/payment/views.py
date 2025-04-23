from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
import hashlib
import urllib.parse
import hmac
import json
import logging
from django.db import transaction
from api.orders.models import Order, OrderItem
from api.cart.models import Cart, CartItem

logger = logging.getLogger(__name__)

class CreateVNPayPayment(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            amount = request.data.get('amount')
            order_id = datetime.now().strftime('%Y%m%d%H%M%S')
            order_desc = f"Thanh toan don hang {order_id}"
            
            try:
                cart = Cart.objects.get(user=request.user)
                if not cart.items.exists():
                    return Response({
                        'error': 'Giỏ hàng trống'
                    }, status=400)
                order = Order.objects.create(
                    user=request.user,
                    order_number=order_id,
                    full_name=request.data.get('full_name'),
                    phone=request.data.get('phone'),
                    email=request.data.get('email'),
                    address=request.data.get('address'),
                    city=request.data.get('city'),
                    total_amount=amount,
                    payment_method='vnpay',
                    payment_status='pending',
                    status='pending'
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

                logger.info(f"Created order {order_id} for VNPay payment")

            except Cart.DoesNotExist:
                return Response({
                    'error': 'Không tìm thấy giỏ hàng'
                }, status=404)
            except Exception as e:
                logger.error(f"Error creating order: {str(e)}")
                return Response({
                    'error': 'Lỗi khi tạo đơn hàng'
                }, status=500)
            vnp_Params = {
                'vnp_Version': settings.VNPAY_VERSION,
                'vnp_Command': settings.VNPAY_COMMAND,
                'vnp_TmnCode': settings.VNPAY_TMN_CODE,
                'vnp_Amount': int(float(amount) * 100),   
                'vnp_CurrCode': settings.VNPAY_CURRENCY_CODE,
                'vnp_TxnRef': order_id,
                'vnp_OrderInfo': order_desc,
                'vnp_OrderType': 'order',
                'vnp_Locale': settings.VNPAY_LOCALE,
                'vnp_ReturnUrl': settings.VNPAY_RETURN_URL,
                'vnp_IpAddr': request.META.get('REMOTE_ADDR', '127.0.0.1'),
                'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S')
            }
            vnp_Params = sorted(vnp_Params.items())
            hash_data = "&".join([f"{urllib.parse.quote_plus(str(key))}={urllib.parse.quote_plus(str(value))}" 
                                for key, value in vnp_Params])
            hmac_obj = hmac.new(settings.VNPAY_HASH_SECRET_KEY.encode('utf-8'), 
                               hash_data.encode('utf-8'), 
                               hashlib.sha512).hexdigest()
            
            vnp_Params.append(('vnp_SecureHash', hmac_obj))
            vnpay_payment_url = f"{settings.VNPAY_PAYMENT_URL}?{hash_data}&vnp_SecureHash={hmac_obj}"
            
            logger.info(f"Created VNPay payment URL for order {order_id}")
            
            return Response({
                'payment_url': vnpay_payment_url,
                'order_id': order_id
            })
            
        except Exception as e:
            logger.error(f"Error creating VNPay payment: {str(e)}")
            return Response({
                'error': 'Không thể tạo thanh toán VNPay'
            }, status=400)