from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),
    path('address/', AddressView.as_view()),
    path('product/', ProductView.as_view()),
    path('cart/add/', AddToCartView.as_view()),
    path('cart/update/<int:cart_item_id>/', UpdateCartItemView.as_view()),
    path('cart/delete/<int:cart_item_id>/', DeleteCartItemView.as_view()),
    path('cart/clear/<int:user_id>/', ClearCartView.as_view()),
    path('order/', OrderView.as_view()),
    path('order-item/', OrderItemView.as_view()),
    path('payment/', PaymentView.as_view()),
    path('logout/', LogoutView.as_view()),

]
