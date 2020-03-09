from rest_framework.renderers import AdminRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.generics import ListAPIView

from shop.models import Product
from shop.serializers import ProductSerializer


class ProductView(APIView):
    """
    View to product
    """
    renderer_classes = [AdminRenderer]
    queryset = ''

    def get(self, request):
        """
        Return product by given id
        :param request: id
        :return: object, if found
        """
        id = request.query_params.get('id', '')
        try:
            product = Product.objects.get(id=id)
        except (ValueError, Product.DoesNotExist):
            return Response("no product with given id", status=HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, many=False)

        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request):
        """
        Create new product by given name and category
        :param request: name, category
        :return: OK status
        """
        name = request.query_params.get('name', '')
        if name == '':
            return Response('name field must be set', status=HTTP_400_BAD_REQUEST)

        category = request.query_params.get('category', '')
        if category == '':
            return Response('category field must be set', status=HTTP_400_BAD_REQUEST)

        product_id = Product.insert(name, category)

        return Response(product_id, status=HTTP_200_OK)

    def put(self, request):
        """
        Update existed product by it's id
        :param request: id, name, category
        :return: OK status
        """
        id = request.query_params.get('id', '')
        try:
            product = Product.objects.get(id=id)
        except (ValueError, Product.DoesNotExist):
            return Response("no product with given id", status=HTTP_404_NOT_FOUND)

        name = request.query_params.get('name', '')
        category = request.query_params.get('category', '')

        if name == '' and category == '':
            return Response('name or category field must be set', status=HTTP_400_BAD_REQUEST)

        if name != '':
            product.name = name

        if category != '':
            product.category = category

        product.save()
        return Response(status=HTTP_200_OK)

    def delete(self, request):
        """
        Delete product by given id
        :param request: id
        :return: OK status
        """
        id = request.query_params.get('id', '')
        try:
            product = Product.objects.get(id=id)
        except (ValueError, Product.DoesNotExist):
            return Response("no product with given id", status=HTTP_404_NOT_FOUND)

        product.remove(id)
        return Response(status=HTTP_200_OK)


class ListProductView(ListAPIView):
    """
    List view to products
    """
    renderer_classes = [AdminRenderer]
    queryset = ''

    def get(self, request, *args, **kwargs):
        """
        Returns list of objects with given name or category
        :param request: name or category
        :param args:
        :param kwargs:
        :return: OK status
        """
        name = request.query_params.get('name', '')
        category = request.query_params.get('category', '')

        if name != '' and category != '':
            objects = Product.objects.filter(name=name, category=category)
        elif name != '':
            objects = Product.objects.filter(name=name)
        elif category != '':
            objects = Product.objects.filter(category=category)
        else:
            objects = Product.objects.all()

        serializer = ProductSerializer(objects, many=True)

        return Response(serializer.data, status=HTTP_200_OK)
