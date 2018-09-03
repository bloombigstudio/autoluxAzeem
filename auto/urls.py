from django.urls import path
from django.conf.urls.static import static

from auto.views import *
from autolux import settings

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('interior', Interior.as_view(), name='interior'),
    path('single/<int:id>', Single.as_view(), name='single'),
    path('about', About.as_view(), name='about'),
    path('contact', Contact.as_view(), name='contact'),

    # Chaipiiii
    path('login', Login.as_view(), name='login'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)