from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Group, Post, User, Follow


def get_page_context(queryset, request):
    paginator = Paginator(queryset, settings.POSTS_QUANTITY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }

@cache_page(20, key_prefix ='index_page')
def index(request):
    template = 'posts/index.html'
    context = get_page_context(Post.objects.all(), request)
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
        'posts': posts,
    }
    context.update(get_page_context(group.posts.all(), request))
    return render(request, template, context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    author = get_object_or_404(User, username=username)
    following = author.following.filter(user_id =request.user.id)
    context = {
        'author': author,
        'following': following,
    }
    context.update(get_page_context(author.posts.all(), request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Posts_detail page method"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None,)
    context = {
        'post': post,
        'form': form,
        'comments': post.comments.all()
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создать новый пост"""
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Редактирование поста"""
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)

@login_required
def add_comment(request, post_id):
    # Получите пост и сохраните его в переменную post.
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    context = get_page_context(
        Post.objects.filter(author__following__user=request.user),
        request
        )
    return render(request, 'posts/follow.html', context)
    # template = 'posts/follow.html'
    # author = get_object_or_404(Post, user=request.user)
    # posts = Post.author.all()

    # template = 'posts/group_list.html'
    # group = get_object_or_404(Group, slug=slug)
    # posts = group.posts.all()
    # context = {
    #     'author': author,
    #     'posts': posts,
    # }
    # context.update(get_page_context(Post.author.all(), request))
    # return render(request, template, context)


# @login_required
# def profile_follow(request, username):
#     # Подписаться на автора
#     author = get_object_or_404(User, username=username)
#     if request.user !=username:
#         Follow.objects.update_or_create(user=request.user, author=author)
#         return redirect('posts:profile', username)
#     else:
#         return redirect('posts:profile', username)

@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    if (
        request.user != author
        and not author.following.filter(user_id=request.user.id).exists()
    ):
        Follow.objects.update_or_create(user=request.user, author=author)
    return redirect('posts:profile', username)

@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author=get_object_or_404(User, username=username)
    if request.user != author:
        following = author.following.filter(user_id=request.user.id)
        if following.exists():
            following.delete()
    return redirect('posts:profile', username=username)


#     # get_object_or_404(
#     #     Follow,
#     #     user= request.user,
#     #     author=User.objects.get(username=username)
#     # )
