# app_name/admin.py
from django.contrib import admin
from .models import Category, Product, Discount, ProductDiscount, Address, Cart, CartItem, Order, OrderItem, Payment

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Discount)
admin.site.register(ProductDiscount)
admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
