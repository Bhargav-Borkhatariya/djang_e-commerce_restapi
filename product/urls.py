from django.urls import path
from product.views import ProductListAPIView, ProductDetailAPIView


urlpatterns = [
    path('', ProductListAPIView.as_view(), name='product_list'),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='product_detail'),
]
