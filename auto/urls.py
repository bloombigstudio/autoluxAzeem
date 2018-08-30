from django.urls import path

from auto.views import *

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('interior', Interior.as_view(), name='interior'),
    path('single', Single.as_view(), name='single'),
    path('about', About.as_view(), name='about'),
    path('contact', Contact.as_view(), name='contact'),
]