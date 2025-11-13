from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import studentserializer, LoginSerializer
from .models import Student
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view
from .models import Cart, Product
from .serializers import CartSerializer, ProductSerializer
from rest_framework import viewsets, status


class StudentApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(request.user)
        students = Student.objects.all()
        serializer = studentserializer(students, many=True)
        return Response({
            "status": True,
            "data": serializer.data
        })


class LoginAPI(APIView):
    def post(self, request):
        data = request.data
        serializer = LoginSerializer(data=data)

        if not serializer.is_valid():
            return Response({
                "status": False,
                "data": serializer.errors,
                "message": "Please provide valid username and password"
            })

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        user_obj = authenticate(username=username, password=password)

        if user_obj is not None:
            token, _ = Token.objects.get_or_create(user=user_obj)
            return Response({
                "status": True,
                "data": {
                    "token": token.key,
                    "username": user_obj.username
                },
                "message": "Login successful"
            })
        else:
            return Response({
                "status": False,
                "data": {},
                "message": "Invalid credentials, please try again."
            })


@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({'error': 'All fields are required'})

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'})

    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(password)
    )

    return Response({
        'message': 'User created successfully',
        'username': user.username
    })

class AddToCartAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"status": False, "message": "Product not found"})

        cart_item, created = Cart.objects.get_or_create(
            user=request.user, product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()

        return Response({
            "status": True,
            "message": f"{product.name} added to cart successfully"
        })

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response({
            "status": True,
            "data": serializer.data
        })
        
        
class ProductAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "data": serializer.data, "message": "Product added successfully"})
        return Response({"status": False, "data": serializer.errors, "message": "Failed to add product"})
    
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    
    
class ProductDeleteView(APIView):
    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return Response({'message': 'Product deleted successfully!'},status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)