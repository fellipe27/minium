from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User
from .models import Post
from django.urls import reverse
from .utils import convert_to_base_64, convert_post_created_date
from django.db.models import Q

def home(request):
    if not request.user.is_authenticated:
        return redirect('/home')

    return render(
        request,
        'blog/home.html',
        { 'user': request.user, 'picture': convert_to_base_64(request.user) }
    )

def search(request, prefix):
    query = request.GET.get('q')
    results = {
        'posts': [
            {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'author': post.author.username,
                'author_picture': convert_to_base_64(post.author)
            } for post in Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
        ],
        'users': [
            {
                'username': user.username,
                'bio': user.bio,
                'photo': convert_to_base_64(user)
            } for user in User.objects.filter(username__icontains=query)
        ]
    }

    return render(
        request,
        'blog/search.html',
        { 'query': query, 'picture': convert_to_base_64(request.user), 'prefix': prefix, 'results': results }
    )

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
                'author_picture': convert_to_base_64(post.author)
            } for post in user_posts
        ]
    except User.DoesNotExist:
        user = None
        posts = None

    return render(
        request,
        'blog/profile.html', {
            'user': user,
            'posts': posts,
            'picture': convert_to_base_64(request.user),
            'photo': convert_to_base_64(user)
        }
    )

def publish(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']

        post = Post.objects.create(title=title, content=content, author=request.user)

        if 'image' in request.FILES:
            post.picture = request.FILES['image'].read()
            post.save()

        return redirect(reverse(
            'view_post',
            kwargs={ 'username': request.user.username, 'post_id': post.id })
        )

    return render(
        request,
        'blog/new_story.html',
        { 'user': request.user, 'picture': convert_to_base_64(request.user) }
    )

def view_post(request, username, post_id):
    user_post = get_object_or_404(Post, id=post_id, author__username=username)

    if request.method == 'POST':
        user_post.delete()

        return redirect('profile', username=username)

    post = {
        'id': user_post.id,
        'title': user_post.title,
        'content': user_post.content,
        'created_at': user_post.created_at.date(),
        'author': user_post.author.username,
        'author_picture': convert_to_base_64(user_post.author),
        'image': convert_to_base_64(user_post)
    }

    return render(
        request,
        'blog/view_post.html',
        { 'post': post, 'picture': convert_to_base_64(request.user), 'username': username }
    )

def user_update(request, username):
    if request.user.username != username:
        return redirect('profile', username=username)

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

    return render(request, 'blog/user_update.html', {
        'user': request.user,
        'picture': convert_to_base_64(request.user)
    })

def post_update(request, username, post_id):
    if request.user.username != username:
        return redirect('profile', username=username)

    post = get_object_or_404(Post, id=post_id, author__username=username)

    if request.method == 'POST':
        post.title = request.POST['title']
        post.content = request.POST['content']

        if 'image' in request.FILES:
            post.picture = request.FILES['image'].read()

        post.save()

        return redirect(reverse(
            'view_post',
            kwargs={'username': request.user.username, 'post_id': post.id}
        ))

    return render(
        request,
        'blog/post_update.html',
        {
            'post': post,
            'picture': convert_to_base_64(request.user)
        }
    )
