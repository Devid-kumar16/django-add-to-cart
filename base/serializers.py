# base/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category, Product, Discount, ProductDiscount,
    Address, Cart, CartItem, Order, OrderItem, Payment
)

User = get_user_model()


# -------------------------
# User Serializer
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


# -------------------------
# Category Serializer
# -------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'name', 'parent_category']


# -------------------------
# Product Serializer
# -------------------------
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = [
            'product_id', 'name', 'description', 'price',
            'stock', 'category', 'category_id', 'created_at'
        ]

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id:
            validated_data['category_id'] = category_id
        return super().create(validated_data)


# -------------------------
# Discount Serializer
# -------------------------
class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = [
            'discount_id', 'code', 'type', 'value',
            'valid_from', 'valid_to', 'is_active'
        ]


# -------------------------
# Address Serializer
# -------------------------
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'address_id', 'user', 'address_line1',
            'address_line2', 'city', 'state', 'pincode',
            'country', 'is_default'
        ]
        read_only_fields = ['user']


# -------------------------
# Cart Item Serializer
# -------------------------
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_id', 'quantity']
        read_only_fields = ['cart']


# -------------------------
# Cart Serializer
# -------------------------
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at']
        read_only_fields = ['user', 'created_at']


# -------------------------
# Order Item Serializer
# -------------------------
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'order_item_id', 'order', 'product', 'product_id',
            'unit_price', 'quantity', 'price'
        ]
        read_only_fields = ['unit_price', 'price', 'order']


# -------------------------
# Order Serializer
# -------------------------
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_id', 'user', 'items', 'total_price',
            'status', 'shipping_address', 'created_at'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        user = self.context['request'].user
        shipping_address = validated_data.get('shipping_address')

        order = Order.objects.create(
            user=user, shipping_address=shipping_address, total_price=0
        )
        total = 0

        for item in items_data:
            product_id = item['product_id']
            qty = item['quantity']
            product = Product.objects.get(product_id=product_id)

            line_price = product.price * qty

            OrderItem.objects.create(
                order=order,
                product=product,
                unit_price=product.price,
                quantity=qty,
                price=line_price
            )

            product.stock = max(product.stock - qty, 0)
            product.save()
            total += line_price

        order.total_price = total
        order.save()
        return order


# -------------------------
# Payment Serializer
# -------------------------
class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = Payment
        fields = [
            'payment_id', 'order', 'method',
            'status', 'amount', 'created_at'
        ]
        read_only_fields = ['created_at']
