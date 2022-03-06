
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('post/create/', views.new_post, name='create_post'),
    path("edit/<str:post_id>", views.edit, name="edit"), 
    path('profile/<str:username>/', views.profile, name='profile'),
    path('following/', views.following, name='following'),
    path("like/<int:id>/", views.like, name="like"),
    path("follow/<int:id>/", views.follow, name="follow"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register")
]
