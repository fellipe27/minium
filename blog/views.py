from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User
from .models import Post
from django.urls import reverse
from PIL import Image
from .utils import convert_to_base_64, convert_post_created_date

def home(request):
    if not request.user.is_authenticated:
        return redirect('/home')

    picture = convert_to_base_64(request.user.picture) if request.user.picture else None

    return render(request, 'blog/home.html', { 'user': request.user, 'picture': picture })

def search(request):
    query = request.GET.get('q')
    picture = convert_to_base_64(request.user.picture) if request.user.picture else None

    return render(request, 'blog/search.html', { 'query': query, 'picture': picture })

def profile(request, username):
    try:
        user = User.objects.get(username=username)
        user_posts = Post.objects.filter(author=user)
        posts = [
            {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'created_at': convert_post_created_date(post.created_at),
                'author': post.author.username,
                'author_picture': convert_to_base_64(post.author.picture) if post.author.picture else None
            } for post in user_posts
        ]
    except User.DoesNotExist:
        user = None
        posts = None

    picture = convert_to_base_64(request.user.picture) if request.user.picture else None
    photo = convert_to_base_64(user.picture) if user.picture else None

    return render(
        request,
        'blog/profile.html', {
            'user': user,
            'posts': posts,
            'picture': picture,
            'photo': photo
        }
    )

def publish(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']

        post = Post.objects.create(title=title, content=content, author=request.user)

        return redirect(reverse(
            'view_post',
            kwargs={ 'username': request.user.username, 'post_id': post.id })
        )

    picture = convert_to_base_64(request.user.picture) if request.user.picture else None

    return render(request, 'blog/new_story.html', { 'user': request.user, 'picture': picture })

def view_post(request, username, post_id):
    user_post = get_object_or_404(Post, id=post_id, author__username=username)
    picture = convert_to_base_64(request.user.picture) if request.user.picture else None

    post = {
        'id': user_post.id,
        'title': user_post.title,
        'content': user_post.content,
        'created_at': user_post.created_at.date(),
        'author': user_post.author.username,
        'author_picture': convert_to_base_64(user_post.author.picture) if user_post.author.picture else None
    }

    return render(
        request,
        'blog/view_post.html', { 'post': post, 'picture': picture }
    )

def user_update(request, username):
    if request.user.username != username:
        return redirect('/')

    if request.method == 'POST':
        user = request.user
        username = request.POST['username']
        bio = request.POST['bio']

        if username:
            user.username = username
        if 'photo' in request.FILES:
            user.picture = request.FILES['photo'].read()

        if bio:
            user.bio = bio
        else:
            user.bio = None

        user.save()

        return redirect('profile', username=username)

    picture = convert_to_base_64(request.user.picture) if request.user.picture else None

    return render(request, 'blog/user_update.html', {
        'user': request.user,
        'picture': picture
    })
