from django.conf.urls import url

from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^$', views.list_of_post, name='list_of_post'),
    url(r'^(?P<slug>[-\w]+)/$', views.post_detail, name='post_detail')
]