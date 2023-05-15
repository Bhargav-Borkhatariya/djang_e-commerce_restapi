import stripe
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, authentication, permissions
from cart.models import Cart, Order, Product, CartItem
from cart.serializers import CartSerializer, CartItemSerializer, OrderSerializer
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY


class CartDetail(APIView):
    authetication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return CartItem.objects.get(pk=pk)
        except CartItem.DoesNotExist:
            return None

    def get(self, request):
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({
                "status": False,
                "message": "Cart not found",
                "data": None,
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart)
        return Response({
            "status": True,
            "message": "Cart items fetched",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                "status": False,
                "message": "Product not found",
                "data": None,
            }, status=status.HTTP_404_NOT_FOUND)

        if product.quantity < quantity:
            return Response({
                "status": False,
                "message": "Insufficient product quantity",
                "data": None,
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            cart = Cart(user=user)
            cart.save()

        try:
            item = cart.items.get(product=product)
            if item.quantity + quantity > product.quantity:
                return Response({
                    "status": False,
                    "message": "Insufficient product quantity",
                    "data": None,
                }, status=status.HTTP_400_BAD_REQUEST)
            item.quantity += quantity
            item.save()
        except CartItem.DoesNotExist:
            item = CartItem(user=user, product=product, quantity=quantity)
            item.save()
            cart.items.add(item)  # Add the CartItem to the items field of the Cart instance
            cart.save()

        serializer = CartSerializer(cart)
        return Response({
            "status": True,
            "message": "Item added to cart",
            "data": serializer.data,
        }, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        cart_item = self.get_object(pk)
        if cart_item is None:
            return Response({
                "status": False,
                "message": "Cart item not found",
                "data": None,
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "Cart item updated successfully",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": False,
                "message": serializer.errors,
                "data": None,
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cart_item = self.get_object(pk)
        if cart_item is None:
            return Response({
                "status": False,
                "message": "Cart item not found",
                "data": None,
            }, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return Response({
            "status": True,
            "message": "Cart item deleted successfully",
            "data": None,
        }, status=status.HTTP_204_NO_CONTENT)


class OrderList(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response({
            "status": True,
            "message": "Orders retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        request.data["user"] = request.user.id
        cart = Cart.objects.get(user=user)
        items_data = [item.id for item in cart.items.all()]
        total = cart.total
        request.data["total"] = total
        request.data["items"] = items_data
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "Order created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": False,
                "message": serializer.errors,
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        order = self.get_object(pk)
        if order is None:
            return Response({
                "status": False,
                "message": "Order not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response({
            "status": True,
            "message": "Order retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        order = self.get_object(pk)
        if order is None:
            return Response({
                "status": False,
                "message": "Order not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "Order updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": False,
                "message": serializer.errors,
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = self.get_object(pk)
        if order is None:
            return Response({
                "status": False,
                "message": "Order not found",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        order.delete()
        return Response({
            "status": True,
            "message": "Order deleted successfully",
            "data": None
        }, status=status.HTTP_204_NO_CONTENT)


class PaymentView(APIView):
    authetication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        # Get the payment details from the POST request
        token = request.data.get('token')
        amount = request.data.get('amount')
        order_id = request.data.get('order_id')  # Assuming you receive the order ID from the frontend

        # Check if the token is valid
        try:
            stripe.Token.retrieve(token)
        except stripe.error.InvalidRequestError:
            return Response({
                'status': False,
                'message': 'Invalid payment information',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create a payment intent using the Stripe API
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='inr',
                payment_method_types=['card'],
                payment_method_data={
                    'type': 'card',
                    'card': {
                        'token': token,
                    },
                },
                description='Example payment',
            )

            # Update the order payment status to "paid"
            order = get_object_or_404(Order, id=order_id)
            order.payment_status = 'paid'
            order.save()

            return Response({
                'status': True,
                'message': 'Payment successful',
                'data': {
                    'client_secret': intent.client_secret
                }
            }, status=status.HTTP_200_OK)

        except stripe.error.CardError as e:
            # The card was declined
            error = e.error
            return Response({
                'status': False,
                'message': error['message'],
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
