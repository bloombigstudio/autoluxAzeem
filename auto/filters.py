import django_filters
from django.forms import TextInput, fields

from auto.models import Product


class ProductFilter(django_filters.FilterSet):
    product_title = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Product
        fields = ['product_title',]
        # fields = {
        #     'product_title': ['icontains'],
        # }


