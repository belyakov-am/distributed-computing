from uuid import UUID

from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view

from django.forms.models import model_to_dict

from shop.models import Product


class ProductView(APIView):
    """
    View to products
    """
    def get(self, request):
        """
        Return product by given id
        :param request: request with id
        :return: object, if found
        """
        id = request.query_params.get('id', '')
        try:
            uuid = UUID(id)
            product = Product.objects.get(id=uuid)
        except (ValueError, Product.DoesNotExist):
            return Response("no product with given id", status=HTTP_404_NOT_FOUND)

        return Response(model_to_dict(product), status=HTTP_200_OK)

    def put(self, request):
        """
        Save product by given name, id, category
        :param request: request with name, id (opt), category
        :return: OK status
        """
        name = request.query_params.get('name', '')
        if name == '':
            return Response('name field must be set', status=HTTP_400_BAD_REQUEST)

        category = request.query_params.get('category', '')
        if category == '':
            return Response('category field must be set', status=HTTP_400_BAD_REQUEST)

        product_id = Product.insert(name, category)

        id = request.query_params.get('id', '')
        if id != '':
            uuid = UUID(id)
            product = Product.objects.get(id=id)
            product.id = uuid
            return Response('inserted with id' + str(uuid), status=HTTP_200_OK)

        return Response('inserted with id' + str(product_id), status=HTTP_200_OK)
