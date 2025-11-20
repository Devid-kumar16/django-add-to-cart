# base/views.py
from django.shortcuts import get_object_or_404
from uuid import UUID
from django.http import Http404

from django.contrib.auth import get_user_model, authenticate
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.routers import DefaultRouter

from .models import (
    Category, Product, Discount, ProductDiscount,
    Address, Cart, CartItem, Order, OrderItem, Payment
)
from .serializers import (
    CategorySerializer, ProductSerializer, DiscountSerializer,
    AddressSerializer, CartSerializer, CartItemSerializer,
    OrderSerializer, PaymentSerializer, UserSerializer
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({'error': 'All fields are required'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    return Response({
        'message': 'User created successfully!',
        'username': user.username
    }, status=201)


class LoginAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get('username')  # kept for compatibility
        password = request.data.get('password')

        if not identifier or not password:
            return Response({"status": False, "message": "username/email and password required"}, status=status.HTTP_400_BAD_REQUEST)

    
        user = authenticate(username=identifier, password=password)
        if user is None:
    
            qs = User.objects.filter(username__iexact=identifier)
            if qs.exists():
                user_candidate = qs.first()
                user = authenticate(username=user_candidate.username, password=password)

        if user is None:
            # try email login
            qs_email = User.objects.filter(email__iexact=identifier)
            if qs_email.exists():
                user_candidate = qs_email.first()
                user = authenticate(username=user_candidate.username, password=password)

        if user is None:
            return Response({"status": False, "message": "Invalid username/email or password."}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"status": True, "message": "Login successful", "data": {"token": token.key, "user": {"id": user.id, "username": user.username}}}, status=status.HTTP_200_OK)



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def apply_discount(self, request, pk=None):
        product = self.get_object()
        code = request.data.get('code')
        if not code:
            return Response({"error": "code required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            discount = Discount.objects.get(code=code, is_active=True)
        except Discount.DoesNotExist:
            return Response({"error": "Discount not found"}, status=status.HTTP_404_NOT_FOUND)
        product.discounts.add(discount)
        return Response({"status": "discount applied"})


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [AllowAny]


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartAddItem(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        qty = request.data.get("quantity", 1)

        # Validate UUID
        try:
            UUID(str(product_id))
        except:
            return Response({"error": "Invalid product_id UUID"}, status=400)

        # Validate quantity
        try:
            qty = int(qty)
            if qty <= 0:
                return Response({"error": "Quantity must be positive"}, status=400)
        except:
            return Response({"error": "Quantity must be integer"}, status=400)

        # Validate product exists
        product = Product.objects.filter(product_id=product_id).first()
        if not product:
            return Response({"error": "Product not found"}, status=404)

        # Get or create cart
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Add or update item
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": qty}
        )
        if not created:
            item.quantity += qty
            item.save()

        return Response(
            {"message": "Item added to cart", "cart_id": str(cart.id)},
            status=200
        )
        
        
class CartUpdateItem(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

        qty = int(request.data.get('quantity', item.quantity))
        if qty <= 0:
            item.delete()
            return Response({"status": "deleted"})
        item.quantity = qty
        item.save()
        return Response({"status": "updated"})



class CreateOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        items = request.data.get('items')  # list of {product_id, quantity}
        shipping_address_id = request.data.get('shipping_address')

        if not items or not isinstance(items, list) or len(items) == 0:
            return Response({"error": "items required (list)"}, status=status.HTTP_400_BAD_REQUEST)

        shipping_address = None
        if shipping_address_id:
            shipping_address = get_object_or_404(Address, address_id=shipping_address_id, user=request.user)

        order = Order.objects.create(user=request.user, total_price=0, shipping_address=shipping_address)
        total = 0

        for it in items:
            pid = it.get('product_id')
            qty = int(it.get('quantity', 1))
            product = get_object_or_404(Product, product_id=pid)

            line_price = product.price * qty
            OrderItem.objects.create(order=order, product=product, unit_price=product.price, quantity=qty, price=line_price)

            # reduce stock safely
            product.stock = max(product.stock - qty, 0)
            product.save()
            total += line_price

        order.total_price = total
        order.save()
        return Response({"message": "order created", "order_id": str(order.order_id)}, status=status.HTTP_201_CREATED)


class OrderListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class PaymentCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id, user=request.user)
        method = request.data.get('method', 'unknown')
        amount = request.data.get('amount') or order.total_price
        status_v = request.data.get('status', 'initiated')

        payment = Payment.objects.create(order=order, method=method, amount=amount, status=status_v)
        # If amount equals total, mark paid
        try:
            if float(amount) == float(order.total_price):
                order.status = 'paid'
                order.save()
        except Exception:
            pass

        return Response({"status": "payment created", "payment_id": str(payment.payment_id)}, status=status.HTTP_201_CREATED)


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'discounts', DiscountViewSet, basename='discount')
router.register(r'addresses', AddressViewSet, basename='address')
