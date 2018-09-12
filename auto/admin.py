from django.contrib import admin

from auto.models import *

admin.site.register(CarCompany)
admin.site.register(CarModel)
admin.site.register(CarYear)
admin.site.register(Product)
admin.site.register(ProductSpecification)

# class CarInline(admin.StackedInline):
#     model = Car
#
#
# class ProductClass(admin.ModelAdmin):
#     inlines = [CarInline]
#
#
# admin.site.register(Product, ProductClass)