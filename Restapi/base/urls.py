from django.urls import path
from .views import (
    StudentApi, LoginAPI, signup, AddToCartAPI,
    ProductAPI, ProductDeleteView,
    CreateOrderAPI, OrderListAPI,CartListAPI,UpdateCartAPI, ProductSearchAPI, ProductListAPI
)

urlpatterns = [
    path('student/', StudentApi.as_view(), name='student'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('signup/', signup, name='signup'),
    path('cart/', AddToCartAPI.as_view(), name='cart'),
    path('product/', ProductAPI.as_view(), name='product'),
    path('product/list/', ProductListAPI.as_view(), name='product-list'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product-delete'),
    path('order/create/', CreateOrderAPI.as_view()),
    path('order/history/<int:user_id>/', OrderListAPI.as_view()),
    path('cart/list/', CartListAPI.as_view()),
    path('cart/update/<int:pk>/', UpdateCartAPI.as_view(), name='cart-update'),
    path('product/search/', ProductSearchAPI.as_view(), name="product-search"),

]
