from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import BaseUserManager
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill
import json

Category_CHOICES = (
    ('Interior', 'INTERIOR'),
    ('Exterior', 'EXTERIOR'),
    ('Mats', 'MATS'),
    ('Detailing', 'DETAILING'),
    ('Leds', 'LEDS'),
    ('Suvs', 'SUVS'),
    ('Utilites', 'UTILITES'),
    ('Others', 'OTHERS'),
)


class ProductColors(models.Model):
    color = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.color


class Product(models.Model):
    product_title = models.CharField(max_length=255)
    product_category = models.CharField(max_length=9, choices=Category_CHOICES, default='EPIC')
    product_image_front = models.ImageField(upload_to='images')
    front_image_thumbnail = ImageSpecField(source='product_image_front',
                                      processors=[ResizeToFill(200, 150)],
                                      format='JPEG',
                                      options={'quality': 50})
    product_image_back = models.ImageField(upload_to='images')
    back_image_thumbnail = ImageSpecField(source='product_image_back',
                                           processors=[ResizeToFill(200, 150)],
                                           format='JPEG',
                                           options={'quality': 50})
    product_price = models.FloatField(null=False,default=0)
    product_discounted_price = models.FloatField(blank=True, null=True)
    product_colors = models.ManyToManyField(ProductColors,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_title


class ProductSpecification(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_related_name')
    product_description = models.CharField(max_length=200)
    product_information = models.CharField(max_length=200)
    product_review = models.CharField(max_length=200)
    first_image = models.ImageField(upload_to='images')
    first_image_thumbnail = ImageSpecField(source='first_image',
                                          processors=[ResizeToFill(200, 150)],
                                          format='JPEG',
                                          options={'quality': 50})
    second_image = models.ImageField(upload_to='images')
    second_image_thumbnail = ImageSpecField(source='second_image',
                                           processors=[ResizeToFill(200, 150)],
                                           format='JPEG',
                                           options={'quality': 50})
    third_image = models.ImageField(upload_to='images')
    third_image_thumbnail = ImageSpecField(source='third_image',
                                           processors=[ResizeToFill(200, 150)],
                                           format='JPEG',
                                           options={'quality': 50})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_id.product_title


class CarCompany(models.Model):
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cars_related_name')
    car_make = models.CharField(max_length=30)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.car_make


class CarModel(models.Model):
    company = models.ForeignKey(CarCompany, on_delete=models.CASCADE, related_name='company_related_name')
    car_model = models.CharField(max_length=30)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.car_model


class CarYear(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cars_related_name',blank=True,null=True)
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='model_related_name')
    car_year = models.CharField(max_length=30)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.model.car_model + " " + self.car_year


class UserWithoutAccount(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Contact Number is not valid")
    contact_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # validators should be a list
    address = models.CharField(max_length=500)
    email = models.EmailField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Online User Order'
        verbose_name_plural = 'Online User Order'

    def __str__(self):
        return self.first_name + " " + self.last_name


class Order(models.Model):
    user = models.ForeignKey(UserWithoutAccount, on_delete=models.CASCADE, related_name='users_without_account')
    item_id = models.CharField(max_length=20)
    item_name = models.CharField(max_length=200)
    item_quantity = models.CharField(max_length=20, default=1)
    item_price = models.CharField(max_length=20)
    total_price = models.CharField(max_length=20, default=0)
    payment_status = models.BooleanField(default=False)
    charge_id = models.CharField(max_length=234, default="None")
    colors = models.CharField(max_length=500, null=True, blank=True)
    order_number = models.CharField(blank=True, null=True, max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_name

    def set_colors(self, colors):
        self.colors = json.dumps(colors)

    def get_colors(self):
        return json.loads(self.colors)


class SliderImage(models.Model):
    main_slider_image = models.ImageField(upload_to='images')
    slider_image_thumbnail = ImageSpecField(source='main_slider_image',
                                           processors=[ResizeToFill(1400, 600)],
                                           format='JPEG',
                                           options={'quality': 50})

    def __str__(self):
        return "Sliding-image-" + str(self.id)


class OrderPageBackground(models.Model):
    background_image = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='Order Page Background')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'created_at'

    def __str__(self):
        return str(self.background_image)


class HomePageCategoriesImages(models.Model):
    led_lights = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='LED LIGHTS')
    interior = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='INTERIOR')
    suv_items = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='SUV ITEMS 4X4')
    exterior = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='EXTERIOR')
    car_detailing = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='CAR DETAILING')
    outdoor_utilities = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='OUTDOOR UTILITIES')
    shop_now = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='SHOP NOW')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'created_at'


class CategoryWiseImageBackground(models.Model):
    interior = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='INTERIOR')
    exterior = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='EXTERIOR')
    mats = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='MATS')
    car_detailing = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='CAR DETAILING')
    led_lights = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='LED LIGHTS')
    suv_items = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='SUV ITEMS 4X4')
    outdoor_utilities = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='OUTDOOR UTILITIES')
    others= models.ImageField(upload_to="images", blank=True, null=True, verbose_name='OTHERS')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'created_at'