from . import views
from django.urls import path

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('like/<slug:slug>', views.PostLike.as_view(), name='post_like'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('posts/', views.UserPostsView.as_view(), name='user_posts'),
    path('post/create/', views.PostCreate.as_view(), name='post_create'),
]
