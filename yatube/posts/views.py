from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from yatube.settings import PAGEVIEW


def _paginator(request, posts):
    paginator = Paginator(posts, PAGEVIEW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=True)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': False})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': True, 'post_id': post.id})


def index(request):
    allposts = Post.objects.all()
    page_obj = _paginator(request, allposts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts = Post.objects.all().filter(group=group)
    page_obj = _paginator(request, group_posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    template_name = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    allposts = Post.objects.filter(author=user)
    page_obj = _paginator(request, allposts)
    post_count = allposts.count()
    context = {
        'author': user,
        'post_count': post_count,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    template_name = 'posts/post_detail.html'
    context = {
        'post': post
    }
    return render(request, template_name, context)
