from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from .models import *
from .serializers import *


class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Signup successful"}, status=201)
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Invalid credentials"}, status=401)

        if check_password(password, user.password_hash):
            return Response({"message": "Login successful", "user_id": user.user_id})
        return Response({"message": "Invalid credentials"}, status=401)


class AddressView(APIView):
    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Address added"}, status=201)
        return Response(serializer.errors, status=400)


class ProductView(APIView):
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product added"}, status=201)
        return Response(serializer.errors, status=400)


class AddToCartView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)
        
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=404)

        cart, created = Cart.objects.get_or_create(user=user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity, "unit_price": product.price}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response({"message": "Item added to cart"}, status=201)


class UpdateCartItemView(APIView):
    def put(self, request, cart_item_id):
        try:
            cart_item = CartItem.objects.get(cart_item_id=cart_item_id)
        except CartItem.DoesNotExist:
            return Response({"message": "Cart item not found"}, status=404)

        cart_item.quantity = request.data.get("quantity", cart_item.quantity)
        cart_item.save()

        return Response({"message": "Cart item updated"}, status=200)


class DeleteCartItemView(APIView):
    def delete(self, cart_item_id):
        try:
            cart_item = CartItem.objects.get(cart_item_id=cart_item_id)
        except CartItem.DoesNotExist:
            return Response({"message": "Cart item not found"}, status=404)

        cart_item.delete()
        return Response({"message": "Item deleted from cart"}, status=200)


class ClearCartView(APIView):
    def delete(self, user_id):
        try:
            cart = Cart.objects.get(user_id=user_id)
        except Cart.DoesNotExist:
            return Response({"message": "Cart not found"}, status=404)

        CartItem.objects.filter(cart=cart).delete()

        return Response({"message": "Cart cleared"}, status=200)


class OrderView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Order created"}, status=201)
        return Response(serializer.errors, status=400)


class OrderItemView(APIView):
    def post(self, request):
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Order item added"}, status=201)
        return Response(serializer.errors, status=400)


class PaymentView(APIView):
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Payment recorded"}, status=201)
        return Response(serializer.errors, status=400)


class LogoutView(APIView):
    def post(self, request):
        return Response({"message": "Logout successful"}, status=200)
