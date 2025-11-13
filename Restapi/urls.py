"""
URL configuration for Restapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from base.views import StudentApi, LoginAPI, signup, AddToCartAPI
from django.http import JsonResponse
from base.views import ProductAPI
from rest_framework.routers import DefaultRouter 
from base.views import ProductViewSet
from base.views import ProductDeleteView
 
router = DefaultRouter()
router.register('products', ProductViewSet)

def home(request):
    return JsonResponse({"message": "Welcome to the API"})
urlpatterns = [
    path('student/', StudentApi.as_view()),
    path('login/', LoginAPI.as_view()),
    path('signup/', signup), 
    path('admin/', admin.site.urls),
    path('cart/', AddToCartAPI.as_view()),
    path('product/', ProductAPI.as_view()),
    path('api/', include(router.urls)),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product-delete'),

]

