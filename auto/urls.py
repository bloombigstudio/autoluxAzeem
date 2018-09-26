from django.conf.urls import url
from django.urls import path
from django.conf.urls.static import static

from auto.views import *
from autolux import settings

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('products/<slug:item_name>', Products.as_view(), name='products'),
    path('single/<int:id>', ProductDescription.as_view(), name='single'),
    path('about', About.as_view(), name='about'),
    path('contact', Contact.as_view(), name='contact'),
    path('place_order', PlaceOrder.as_view(), name='place_order'),
    path('car_information', CarInformation.as_view(), name='car_information'),
    url(r'verifyforzoho.html/$', ZohoView.as_view(), name='zoho'),

    # Chaipiiii
    path('login', Login.as_view(), name='login'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)