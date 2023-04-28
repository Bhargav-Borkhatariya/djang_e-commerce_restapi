from django.urls import path
from product.views import ProductListAPIView, ProductDetailAPIView, ProductFilterAPIView


urlpatterns = [
    path('', ProductListAPIView.as_view(), name='product_list'),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='product_detail'),
    path('filter/', ProductFilterAPIView.as_view(), name='product-filter'),
]
