from django.contrib import admin

from auto.models import *


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    max_num = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductSpecificationInline]


admin.site.register(Product, ProductAdmin)


class OrdersInline(admin.TabularInline):
    model = Order


class UsersAdmin(admin.ModelAdmin):
    inlines = [OrdersInline]


admin.site.register(UserWithoutAccount, UsersAdmin)


class CarModelline(admin.TabularInline):
    model = CarModel


class CarCompanyAdmin(admin.ModelAdmin):
    inlines = [CarModelline]


admin.site.register(CarCompany, CarCompanyAdmin)

admin.site.register(CarYear)

