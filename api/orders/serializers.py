from rest_framework import serializers
from .models import Order, OrderItem, Payment
from api.products.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment 
        fields = ['id', 'payment_id', 'amount', 'status', 'created_at','raw_response']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'full_name', 
            'phone', 'email', 'address', 'city',
            'total_amount', 'payment_method', 'payment_status',
            'status', 'order_note', 'created_at', 'items', 'payments'
        ]
        read_only_fields = ['order_number', 'user', 'total_amount']