from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .utilities import get_paginator

CACHE_TIME = 20


@cache_page(CACHE_TIME)
def index(request):
    post_list = Post.objects.select_related('author', 'group')
    return render(request, 'posts/index.html', context={
        'title': 'Последние обновления на сайте',
        'page_obj': get_paginator(post_list, request), }
                  )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    return render(request, 'posts/group_list.html', context={
        'group': group,
        'page_obj': get_paginator(post_list, request), }
                  )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group')
    posts_count = post_list.count()
    following = request.user.is_authenticated
    if following:
        following = author.following.filter(user=request.user).exists()
    return render(request, 'posts/profile.html', context={
        'author': author,
        'posts_count': posts_count,
        'following': following,
        'page_obj': get_paginator(post_list, request), }
                  )


def post_detail(request, post_id):
    post_item = get_object_or_404(
        Post.objects.select_related('group', 'author'), pk=post_id
    )
    form = CommentForm()
    comments = post_item.comments.select_related('author')
    return render(request, 'posts/post_detail.html', context={
        'post_item': post_item,
        'form': form,
        'comments': comments}
                  )


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None
                    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context={
            'form': form, 'is_edit': False}
                      )
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    user_name = request.user.username
    return redirect('posts:profile', user_name)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post
                    )
    if post.author == request.user:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', context={
        'form': form, 'is_edit': True}
                  )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author'),
        pk=post_id
    )
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follow_posts = Post.objects.filter(author__following__user=request.user)
    return render(request, 'posts/follow.html', context={
        'title': 'Посты с подписками',
        'page_obj': get_paginator(follow_posts, request), }
                  )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)

@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
