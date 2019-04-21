from django.shortcuts import render, get_object_or_404

from auto.filters import ProductFilter
from auto.models import Product
from blog.models import Post

product_list = Product.objects.all()

def list_of_post(request):
    post = Post.objects.filter(status='published')
    template = 'blog/post/list_of_post.html'
    product_filter = ProductFilter(request.GET, queryset=product_list)
    context = { 'post': post, 'filter': product_filter }
    return render(request, template, context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    template = 'blog/post/post_detail.html'
    product_filter = ProductFilter(request.GET, queryset=product_list)
    context = {'post': post, 'filter': product_filter}
    return render(request, template, context)