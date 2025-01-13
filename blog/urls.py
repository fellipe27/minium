from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('new-story/', views.publish, name='new_story'),
    path('@<str:username>/', views.profile, name='profile'),
    path('@<str:username>/<uuid:post_id>/', views.view_post, name='view_post'),
    path('@<str:username>/update/', views.user_update, name='update')
]
