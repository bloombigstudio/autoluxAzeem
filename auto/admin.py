from django.contrib import admin

from auto.models import *
from blog.models import Post


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    max_num = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductSpecificationInline]


class OrdersInline(admin.TabularInline):
    model = Order


class UsersAdmin(admin.ModelAdmin):
    inlines = [OrdersInline]


class CarModelline(admin.TabularInline):
    model = CarModel


class CarCompanyAdmin(admin.ModelAdmin):
    inlines = [CarModelline]


class CarYearAdmin(admin.ModelAdmin):
    list_display = ('product', 'model', 'car_year')


class HomePageCategoriesImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'led_lights', 'interior', 'suv_items', 'exterior', 'car_detailing', 'outdoor_utilities')


class CategoryWiseImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'interior', 'exterior', 'mats', 'car_detailing', 'led_lights', 'suv_items' , 'outdoor_utilities', 'others')


admin.site.register(CarCompany, CarCompanyAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(CarYear, CarYearAdmin)
admin.site.register(SliderImage)
admin.site.register(ProductColors)
admin.site.register(UserWithoutAccount, UsersAdmin)
admin.site.register(OrderPageBackground)
admin.site.register(HomePageCategoriesImages, HomePageCategoriesImagesAdmin)
admin.site.register(CategoryWiseImageBackground, CategoryWiseImagesAdmin)
admin.site.register(Post)


