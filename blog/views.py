from django.shortcuts import render, get_object_or_404
from blog.models import Post


def list_of_post(request):
    post = Post.objects.filter(status='published')
    template = 'blog/post/list_of_post.html'
    context = { 'post': post }
    return render(request, template, context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    template = 'blog/post/post_detail.html'
    context = {'post': post}
    return render(request, template, context)