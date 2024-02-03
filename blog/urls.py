from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),  
    path('logout/', views.user_logout, name='logout'),  
    path('signup/', views.signup, name='signup'), 
    path('upload/', views.upload_photo, name='upload_photo'), 
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
]