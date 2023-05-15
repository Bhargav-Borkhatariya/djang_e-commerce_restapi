from django.urls import path
from cart.views import CartDetail, PaymentView, OrderList, OrderDetail

urlpatterns = [
    path('', CartDetail.as_view(), name='cart-list'),
    path('<int:pk>/', CartDetail.as_view(), name='cart-detail'),
    path('orders/', OrderList.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetail.as_view(), name='order-detail'),
    path('payment/', PaymentView.as_view(), name='payment'),
]
