from . import views
from django.urls import path

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('myposts/', views.UserPostsView.as_view(), name='user_posts'),
    path('post/<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('like/<slug:slug>', views.PostLike.as_view(), name='post_like'),
    path('post/create/', views.PostCreate.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', views.PostUpdate.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDelete.as_view(), name='post_delete'),
]
