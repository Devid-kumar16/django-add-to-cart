from rest_framework import serializers
from .models import Student
from .models import Cart, Product

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
        fields = ['id', 'name', 'price']

class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'product', 'quantity', 'created_at']