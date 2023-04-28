from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_204_NO_CONTENT,
    HTTP_200_OK,
)
from product.models import Product
from product.serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


class ProductListAPIView(APIView):
    """
    API View for listing all products or search product or creating a new product.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search_query = request.query_params.get('search', None)
        if search_query:
            products = Product.objects.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(category__name__iexact=search_query)
            )
        else:
            products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "status": True,
                "message": "Product created successfully",
                "data": serializer.data,
            }, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    """
    API View for retrieving, updating, or deleting a product instance.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            product = Product.objects.get(pk=pk, user=self.request.user)
            return product
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if product is not None:
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        return Response({
            "status": False,
            "message": "Product not found",
            "data": None,
        }, status=HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        product = self.get_object(pk)
        if product is not None:
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({
                    "status": True,
                    "message": "Product updated successfully",
                    "data": serializer.data,
                })
            return Response(serializer.rors, status=HTTP_400_BAD_REQUEST)
        return Response({
            "status": False,
            "message": "Product not found",
            "data": None,
        }, status=HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        product = self.get_object(pk)
        if product is not None:
            product.delete()
            return Response({
                "status": True,
                "message": "Product deleted successfully",
                "data": None,
            }, status=HTTP_204_NO_CONTENT)
        return Response({
            "status": False,
            "message": "Product not found",
            "data": None,
        }, status=HTTP_404_NOT_FOUND)


class ProductFilterAPIView(APIView):
    """
    API View for filtering products by category, price, and other attributes.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.query_params.get('category')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        other_attrs = {}
        for param in request.query_params:
            if param not in ['category', 'min_price', 'max_price']:
                other_attrs[param] = request.query_params.get(param)

        products = Product.objects.all()

        if category:
            products = products.filter(category=category)

        if min_price:
            products = products.filter(price__gte=min_price)

        if max_price:
            products = products.filter(price__lte=max_price)

        if other_attrs:
            query = Q()
            for key, value in other_attrs.items():
                query &= Q(**{key: value})
            products = products.filter(query)

        serializer = ProductSerializer(products, many=True)
        return Response({
            "status": True,
            "message": "Product List",
            "data": serializer.data,
        }, status=HTTP_200_OK)
