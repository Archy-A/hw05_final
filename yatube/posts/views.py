from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment
from yatube.settings import PAGEVIEW


def _paginator(request, posts):
    paginator = Paginator(posts, PAGEVIEW)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
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
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
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
    form = CommentForm(request.POST or None)
    template_name = 'posts/post_detail.html'
    comments = post.comments.all()
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, template_name, context)

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # user = post.author
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    # posts = user.author_posts.all()
    is_edit = request.user == post.author
    # count_posts = posts.count()
    context = {
        # 'count_posts': count_posts,
        'post': post,
        'is_edit': is_edit,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    return redirect('posts:post_detail', post_id=post_id)