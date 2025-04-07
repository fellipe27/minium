from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('search/posts/', views.search_page, { 'prefix': 'posts' }, name='search_posts'),
    path('search/users/', views.search_page, { 'prefix': 'users' }, name='search_users'),
    path('new-story/', views.new_story_page, name='new_story'),
    path('@<str:username>/<uuid:post_id>/', views.view_post_page, name='view_post'),
    path('@<str:username>/', views.profile_page, name='profile'),
    path('@<str:username>/update/', views.update_user_page, name='update_user'),
    path('@<str:username>/<uuid:post_id>/delete/', views.delete_post, name='delete_post'),
    path('@<str:username>/<uuid:post_id>/update/', views.update_post_page, name='update_post'),
    path('@<str:username>/<uuid:post_id>/claps/', views.like_or_unlike_post, name='clap_post')
]
