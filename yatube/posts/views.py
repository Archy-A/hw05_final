from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow
from yatube.settings import PAGEVIEW
from django.views.decorators.cache import cache_page
from django.core.cache import cache


def _paginator(request, posts):
    paginator = Paginator(posts, PAGEVIEW)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=True)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=request.user)
    return render(request, "posts/create_post.html", {"form": form, "is_edit": False})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id=post_id)
    return render(
        request,
        "posts/create_post.html",
        {"form": form, "is_edit": True, "post_id": post.id},
    )


def index(request):
    template = "posts/index.html"
    if "index_page" in cache:
        post_list = cache.get("index_page")
    else:
        post_list = Post.objects.all()
        cache.set("index_page", post_list, 20)
    page_obj = _paginator(request, post_list)
    context = {
        "page_obj": page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts = Post.objects.all().filter(group=group)
    page_obj = _paginator(request, group_posts)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    template_name = "posts/profile.html"
    author = get_object_or_404(User, username=username)
    me = request.user
    allposts = Post.objects.filter(author=author)
    page_obj = _paginator(request, allposts)
    post_count = allposts.count()
    if request.user.is_authenticated:
        following = Follow.objects.filter(author=author, user=me).exists()
    else:
        following = False
    context = {
        "author": author,
        "post_count": post_count,
        "page_obj": page_obj,
        "following": following,
    }
    return render(request, template_name, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    is_edit = request.user == post.author
    context = {
        "post": post,
        "is_edit": is_edit,
        "comments": comments,
        "form": form,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("posts:post_detail", post_id=post_id)
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    authors = Follow.objects.filter(user=user)
    alla = [i.author for i in authors]
    allposts = Post.objects.filter(author__in=alla)

    page_obj = _paginator(request, allposts)
    context = {
        "author": user,
        "page_obj": page_obj,
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    auth = get_object_or_404(User, username=username)
    user = request.user
    if user == auth or Follow.objects.filter(user=user, author=auth).exists():
        return redirect("posts:index")
    else:
        Follow.objects.create(user=user, author=auth)
        return redirect("posts:follow_index")


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect("posts:index")
