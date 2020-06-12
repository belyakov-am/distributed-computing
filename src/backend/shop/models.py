import uuid

from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=256, help_text='name of the product')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text='product id')
    category = models.CharField(max_length=256, help_text="product's category")

    def __str__(self):
        return self.name

    @staticmethod
    def get_by_id(product_id):
        return Product.objects.get(id=product_id)

    @staticmethod
    def insert(name, category):
        product = Product(name=name, category=category)
        product.save()
        return product.id

    @staticmethod
    def remove(product_id):
        product = Product.objects.get(id=product_id)
        product.delete()

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Product'
