from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .forms import SignUpForm, PostForm
from django.utils import timezone
from .models import Post, Follow, User, Like
from django.urls import reverse
from django.db import models


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to a home or dashboard page
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            # Check if the user has already posted today
            if not Post.objects.filter(user=request.user, created_at__date=timezone.now().date()).exists():
                post.save()
                return redirect('home')  # Redirect to a page where the post is displayed
            else:
                form.add_error(None, "You can only post once per day.")
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})


def home(request):
    posts = Post.objects.all().order_by('-created_at')  # Latest posts first
    return render(request, 'your_app/home.html', {'posts': posts})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        if 'comment_submit' in request.POST:  # Check if the comment form was submitted
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.user = request.user
                comment.save()
                return redirect('post_detail', post_id=post.id)
        elif 'like_submit' in request.POST:  # Simple like implementation
            _, created = Like.objects.get_or_create(post=post, user=request.user)
            if not created:
                # If the like already existed, remove it
                Like.objects.filter(post=post, user=request.user).delete()
            return redirect('post_detail', post_id=post.id)
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comment_form': comment_form,
        'comments': post.comments.all(),  # Assuming your Comment model has a 'post' foreign key
    })


def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            # Handle category assignment
            categories = form.cleaned_data['categories']
            for category in categories:
                PostCategory.objects.create(post=post, category=category)
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'your_app/post_form.html', {'form': form})


@login_required
def follow_user(request, user_id):
    user_to_follow = User.objects.get(pk=user_id)
    _, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
    if created:
        # Logic if the follow is successful, e.g., send a notification
        pass
    return HttpResponseRedirect(reverse('user_profile', args=[user_id]))

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = User.objects.get(pk=user_id)
    Follow.objects.filter(follower=request.user, followed=user_to_unfollow).delete()
    return HttpResponseRedirect(reverse('user_profile', args=[user_id]))


def home(request):
    # Get the list of ids for users that the current user follows
    user_ids = request.user.following.values_list('followed__id', flat=True)
    # Filter posts to only include those from followed users
    posts = Post.objects.filter(user__id__in=user_ids).order_by('-created_at')
    return render(request, 'your_app/home.html', {'posts': posts})


def notifications(request):
    notifications = request.user.notifications.filter(is_read=False)
    return render(request, 'your_app/notifications.html', {'notifications': notifications})

