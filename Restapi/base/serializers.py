from rest_framework import serializers
from .models import Student
from .models import Cart, Product, Order, OrderItem

class studentserializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        
        
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'created_at', 'items']
        
        
class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    

    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'quantity', 'created_at']
