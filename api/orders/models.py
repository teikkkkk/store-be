from django.db import models
from django.contrib.auth import get_user_model
from api.products.models import Product

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang giao hàng'),
        ('completed', 'Đã giao hàng'),
        ('cancelled', 'Đã hủy'),
    )

    PAYMENT_METHOD = (
        ('cod', 'Thanh toán khi nhận hàng'),
        ('vnpay', 'Thanh toán qua VNPay'),
    )

    PAYMENT_STATUS = (
        ('pending', 'Chờ thanh toán'),
        ('completed', 'Đã thanh toán'),
        ('failed', 'Thanh toán thất bại'),
        ('refunded', 'Đã hoàn tiền'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.order_number}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    
    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(max_length=100)  
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    raw_response = models.JSONField()  

    def __str__(self):
        return f'Payment {self.payment_id} for Order {self.order.order_number}'