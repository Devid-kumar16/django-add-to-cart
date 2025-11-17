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
from django.db.models import Q
from .serializers import CartSerializer, ProductSerializer
from rest_framework import viewsets, status
from .models import Cart, Order, OrderItem
from .serializers import OrderSerializer
from rest_framework.generics import ListAPIView


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


from rest_framework import status

class LoginAPI(APIView):
    def post(self, request):
        data = request.data
        serializer = LoginSerializer(data=data)

        # Input validation error → 400 Bad Request
        if not serializer.is_valid():
            return Response({
                "status": False,
                "errors": serializer.errors,
                "message": "Invalid input. Please enter a valid username and password."
            }, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        # Username check → 401 Unauthorized
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({
                "status": False,
                "message": "The username you entered does not exist."
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Password check → 401 Unauthorized
        user_obj = authenticate(username=username, password=password)
        if user_obj is None:
            return Response({
                "status": False,
                "message": "Incorrect password. Please try again."
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Successful login → 200 OK
        token, _ = Token.objects.get_or_create(user=user_obj)

        return Response({
            "status": True,
            "message": "Login successful",
            "data": {
                "token": token.key,
                "user": {
                    "id": user_obj.id,
                    "username": user_obj.username,
                }
            }
        }, status=status.HTTP_200_OK)



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

        # If request.data is a list → add multiple products
        if isinstance(request.data, list):
            serializer = ProductSerializer(data=request.data, many=True)
        else:
            serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "data": serializer.data,
                "message": "Product(s) added successfully"
            }, status=201)

        return Response({
            "status": False,
            "data": serializer.errors,
            "message": "Failed to add product"
        }, status=400)

    
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    

class ProductListAPI(ListAPIView):
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
        
        
class CreateOrderAPI(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        items = request.data.get("items")

        if not user_id or not items:
            return Response({"error": "user_id and items are required"}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        order = Order.objects.create(user=user, total_price=0)

        total_price = 0

        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"error": f"Product {product_id} not found"}, status=404)

            price = product.price * quantity
            total_price += price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )
            
        order.total_price = total_price
        order.save()

        return Response({
            "message": "Order created successfully",
            "order": OrderSerializer(order).data
        }, status=201)


class OrderListAPI(APIView):
    def get(self, request, user_id):
        try:
            orders = Order.objects.filter(user_id=user_id)
        except:
            return Response({"error": "Invalid user"}, status=400)

        return Response(OrderSerializer(orders, many=True).data)


class CartListAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)


class UpdateCartAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            cart_item = Cart.objects.get(id=pk, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=404)

        quantity = request.data.get("quantity")

        if not quantity:
            return Response({"error": "Quantity is required"}, status=400)

        cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Cart updated successfully"})
    
    
class ProductSearchAPI(APIView):
    def get(self, request):
        keyword = request.GET.get('keyword', '')
        category = request.GET.get('category', '')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')

        products = Product.objects.all()

        if keyword:
            products = products.filter(
                Q(name__icontains=keyword) | Q(description__icontains=keyword)
            )

        if category:
            products = products.filter(category__icontains=category)

        if min_price:
            products = products.filter(price__gte=min_price)

        if max_price:
            products = products.filter(price__lte=max_price)

        serializer = ProductSerializer(products, many=True)
        return Response({
            "status": True,
            "count": len(serializer.data),
            "results": serializer.data
        }, status=status.HTTP_200_OK)