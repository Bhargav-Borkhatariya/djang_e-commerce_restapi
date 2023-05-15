from rest_framework import serializers
from product.serializers import ProductSerializer
from cart.models import Cart, CartItem, Order


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    total = serializers.SerializerMethodField()

    def get_total(self, obj):
        # Calculate the total price of all items in the cart
        total_price = sum([item.product.price * item.quantity for item in obj.items.all()])
        # Return the total as a string with 2 decimal places
        return "{:.2f}".format(total_price)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total']


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total', 'created_at', 'status', 'shipping_address', 'payment_method', 'payment_status']
        read_only_fields = ['id', 'created_at']

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        items = instance.items.all()
        items = list(items)

        instance.status = validated_data.get('status', instance.status)
        instance.shipping_address = validated_data.get('shipping_address', instance.shipping_address)
        instance.payment_method = validated_data.get('payment_method', instance.payment_method)
        instance.payment_status = validated_data.get('payment_status', instance.payment_status)
        instance.save()

        for item_data in items_data:
            item = items.pop(0)
            item.quantity = item_data.get('quantity', item.quantity)
            item.save()

        return instance