from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/posts/', views.search, { 'prefix': 'posts' }, name='search'),
    path('search/users/', views.search, { 'prefix': 'users' }, name='search_users'),
    path('new-story/', views.publish, name='new_story'),
    path('@<str:username>/', views.profile, name='profile'),
    path('@<str:username>/update/', views.user_update, name='update'),
    path('@<str:username>/<uuid:post_id>/', views.view_post, name='view_post'),
    path('@<str:username>/<uuid:post_id>/update/', views.post_update, name='post_update')
]
