from django.shortcuts import render, redirect
from accounts.models import User
from .models import Post, Comment
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from pathlib import Path
from django.conf import settings
from .utils import convert_post, convert_user, get_post_keywords
from django.db.models import Q

def home_page(request):
    if not request.user.is_authenticated:
        return redirect('landing:landing')

    query = request.GET.get('feed')

    if query:
        users_followed = [user for user in request.user.following.all()]
        posts = [
            convert_post(post, request.user)
            for post in Post.objects.filter(author__in=users_followed).order_by('-created_at')
        ]
    else:
        user_interests = request.session.get('interests', [])
        filtered_posts = [
            post for post in Post.objects.all().order_by('-created_at')
            if any(keyword in user_interests for keyword in get_post_keywords(post))
            and request.user.id != post.author.id
        ]

        posts = [convert_post(post, request.user) for post in filtered_posts]

    return render(request, 'blog/home_page.html', {
        'user': convert_user(request.user),
        'query': query,
        'posts': posts
    })

def search_page(request, prefix):
    query = request.GET.get('q')
    results = {
        'posts': [
            convert_post(post, request.user)
            for post in Post.objects.filter(Q(title__icontains=query) | Q(story__icontains=query))
        ],
        'users': [
            {
                'data': convert_user(user),
                'is_followed': request.user.is_following(user)
            }
            for user in User.objects.filter(username__icontains=query)
        ]
    }

    if request.method == 'POST':
        user_id = request.POST['user_id']
        user = get_object_or_404(User, id=user_id)

        if not request.user.is_following(user):
            request.user.follow(user)
        else:
            request.user.unfollow(user)

        return redirect(f'{request.path}?q={query}')

    return render(request, 'blog/search_page.html', {
        'user': convert_user(request.user), 'prefix': prefix, 'query': query, 'results': results
    })

def new_story_page(request):
    if request.method == 'POST':
        title = request.POST['title']
        story = request.POST['story']

        post = Post.objects.create(title=title, story=story, author=request.user)

        if 'image' in request.FILES:
            post.picture = request.FILES['image'].read()
        else:
            default_image_path = Path(settings.BASE_DIR) / 'blog' / 'static' / 'blog' / 'images' / 'default-image.png'

            with open(default_image_path, 'rb') as f:
                post.picture = f.read()

        post.save()

        return redirect(reverse(
            'blog:view_post', kwargs={ 'username': request.user.username, 'post_id': post.id }
        ))

    return render(request, 'blog/new_story_page.html', {
        'user': convert_user(request.user),
        'is_new_post': True
    })

def view_post_page(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)

    if request.method == 'POST':
        comment = request.POST['comment']
        Comment.objects.create(content=comment, post=post, author=request.user)

        return redirect(reverse(
            'blog:view_post', kwargs={ 'username': username, 'post_id': post_id }
        ))

    keywords = get_post_keywords(post)
    interests = request.session.get('interests', [])
    interests = list(set(interests) | set(keywords))

    request.session['interests'] = interests

    return render(
        request,
        'blog/view_post_page.html',
        {
            'post': convert_post(post, request.user),
            'user': convert_user(request.user),
            'owner': convert_user(post.author)
        }
    )

def profile_page(request, username):
    try:
        user = User.objects.get(username=username)
        user_posts = Post.objects.filter(author=user)
        posts = [convert_post(post, user) for post in user_posts]
    except User.DoesNotExist:
        user = None
        posts = None

    if request.method == 'POST':
        if not request.user.is_following(user):
            request.user.follow(user)
        else:
            request.user.unfollow(user)

        return redirect('blog:profile', username=user.username)

    return render(
        request,
        'blog/profile_page.html',
        {
            'user': convert_user(request.user),
            'posts': posts,
            'profile_owner': {
                'data': convert_user(user),
                'is_followed': request.user.is_following(user)
            }
        }
    )

def update_user_page(request, username):
    if request.user.username != username:
        return redirect('blog:profile', username=username)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    if request.method == 'POST':
        bio = request.POST['bio']

        if 'image' in request.FILES:
            user.picture = request.FILES['image'].read()

        user.bio = bio
        user.save()

        return redirect('blog:profile', username=user.username)

    return render(request, 'blog/update_user_page.html', { 'user': convert_user(user) })

def update_post_page(request, username, post_id):
    if request.user.username != username:
        return redirect(reverse(
            'blog:view_post', kwargs={ 'username': username, 'post_id': post_id }
        ))

    post = get_object_or_404(Post, id=post_id, author__username=username)

    if request.method == 'POST':
        post.title = request.POST['title']
        post.story = request.POST['story']

        if 'image' in request.FILES:
            post.picture = request.FILES['image'].read()

        post.save()

        return redirect(reverse(
            'blog:view_post', kwargs={ 'username': username, 'post_id': post.id }
        ))

    return render(
        request,
        'blog/new_story_page.html',
        { 'post': convert_post(post, request.user), 'user': convert_user(post.author), 'is_new_post': False }
    )

def delete_post(request, username, post_id):
    if request.user.username == username:
        post = get_object_or_404(Post, id=post_id, author__username=username)
        post.delete()

    return redirect('blog:profile', username=username)

def like_or_unlike_post(request, username, post_id):
    if request.user.username != username:
        post = get_object_or_404(Post, id=post_id, author__username=username)

        if post.user_liked_post(request.user):
            post.unlike_post(request.user)
        else:
            post.like_post(request.user)

    return redirect(reverse(
        'blog:view_post', kwargs={ 'username': username, 'post_id': post_id }
    ))
