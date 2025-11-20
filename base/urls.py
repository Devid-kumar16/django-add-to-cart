from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ProductViewSet, DiscountViewSet,
    AddressViewSet, CartView, CartAddItem, CartUpdateItem,
    CreateOrderAPI, OrderListAPI, PaymentCreateAPI,
    signup, LoginAPI
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'discounts', DiscountViewSet, basename='discount')
router.register(r'addresses', AddressViewSet, basename='address')


urlpatterns = [
    path('', include(router.urls)),
    path('signup/', signup, name='signup'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartAddItem.as_view(), name='cart-add'),
    path('cart/item/<uuid:item_id>/', CartUpdateItem.as_view(), name='cart-item-update'),
    path('orders/create/', CreateOrderAPI.as_view(), name='create-order'),
    path('orders/', OrderListAPI.as_view(), name='orders-list'),
    path('orders/<uuid:order_id>/pay/', PaymentCreateAPI.as_view(), name='order-pay'),
]