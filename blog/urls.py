from . import views
from django.urls import path, include
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def permission_denied_view(request, exception):
    return redirect('login')

handler403 = permission_denied_view


urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('myposts/', views.UserPostsView.as_view(), name='user_posts'),
    path('post/create/', views.PostCreate.as_view(), name='post_create'),
    path('post/<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('login/', LoginView.as_view(template_name='account/login.html'), name='login'),
    path('like/<slug:slug>', views.PostLike.as_view(), name='post_like'),
    path('post/<int:pk>/edit/', views.PostUpdate.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDelete.as_view(), name='post_delete'),
    path('comment/edit/<int:comment_id>/', views.edit_comment, name='comment_edit'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='comment_delete'),
]
