from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_204_NO_CONTENT,
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
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
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
