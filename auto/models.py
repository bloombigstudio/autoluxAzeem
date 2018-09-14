from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import BaseUserManager

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

class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)




class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email


class Product(models.Model):
    product_title = models.CharField(max_length=30)
    product_category = models.CharField(max_length=9, choices=Category_CHOICES, default='EPIC')
    product_image_front = models.ImageField(upload_to='images')
    product_image_back = models.ImageField(upload_to='images')
    product_price = models.CharField(max_length=30)
    product_discounted_price = models.CharField(max_length=30,default=None, blank=True, null=True)
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
    second_image = models.ImageField(upload_to='images')
    third_image = models.ImageField(upload_to='images')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_id.product_title


class CarCompany(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cars_related_name')
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
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='model_related_name')
    car_year = models.CharField(max_length=30)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.model.car_model + " " + self.car_year


class UserWithoutAccount(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    contact_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # validators should be a list
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=30)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name


class Order(models.Model):
    user = models.ForeignKey(UserWithoutAccount, on_delete=models.CASCADE, related_name='users_without_account')
    item_id = models.CharField(max_length=20)
    item_name = models.CharField(max_length=200)
    item_price = models.CharField(max_length=20)
    payment_status = models.BooleanField(default=False)
    charge_id = models.CharField(max_length=234, default="None")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.item_name
