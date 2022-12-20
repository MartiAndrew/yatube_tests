# from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User
from .forms import PostForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .utilities import get_paginator


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    return render(request, 'posts/index.html', context={
        'title': 'Последние обновления на сайте',
        'page_obj': get_paginator(post_list, request), })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    return render(request, 'posts/group_list.html', context={
        'group': group,
        'page_obj': get_paginator(post_list, request), })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group')
    posts_count = post_list.count()
    return render(request, 'posts/profile.html', context={
        'author': author,
        'posts_count': posts_count,
        'page_obj': get_paginator(post_list, request), })


def post_detail(request, post_id):
    post_item = get_object_or_404(
        Post.objects.select_related('group', 'author'), pk=post_id)
    return render(request, 'posts/post_detail.html', context={
        'post_item': post_item})


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context={
            'form': form, 'is_edit': False})
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    user_name = request.user.username
    return redirect('posts:profile', user_name)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if post.author == request.user:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', context={
        'form': form, 'is_edit': True})