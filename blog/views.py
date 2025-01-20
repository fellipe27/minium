from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User
from .models import Post, Comment
from django.urls import reverse
from .utils import convert_to_base_64, convert_post_created_date, get_post_keywords, create_post_object
from django.db.models import Q
from pathlib import Path
from django.conf import settings

def home(request):
    if not request.user.is_authenticated:
        return redirect('landing:landing')

    query = request.GET.get('feed')

    if query:
        users_followed = [user for user in request.user.following.all()]
        posts = [
            create_post_object(post)
            for post in Post.objects.filter(author__in=users_followed).order_by('-created_at')
        ]
    else:
        user_interests = request.user.interests
        filtered_posts = [
            post for post in Post.objects.all().order_by('-created_at')
            if any(keyword in user_interests for keyword in post.keywords)
            and request.user.id != post.author.id
        ]

        posts = [create_post_object(post) for post in filtered_posts]

    return render(
        request,
        'blog/home.html',
        {
            'user': request.user,
            'picture': convert_to_base_64(request.user),
            'query': query,
            'posts': posts
        }
    )

def search(request, prefix):
    if not request.user.is_authenticated:
        return redirect('blog:home')

    query = request.GET.get('q')
    results = {
        'posts': [
            create_post_object(post)
            for post in Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
        ],
        'users': [
            {
                'id': user.id,
                'username': user.username,
                'bio': user.bio,
                'photo': convert_to_base_64(user),
                'is_followed': request.user.is_following(user)
            } for user in User.objects.filter(username__icontains=query)
        ]
    }

    if request.method == 'POST' and 'user_id' in request.POST:
        user_id = request.POST['user_id']
        user = get_object_or_404(User, id=user_id)

        if not request.user.is_following(user):
            request.user.follow(user)
        else:
            request.user.unfollow(user)

        return redirect(f'{request.path}?q={query}')

    return render(
        request,
        'blog/search.html',
        { 'query': query, 'picture': convert_to_base_64(request.user), 'prefix': prefix, 'results': results }
    )

def profile(request, username):
    if not request.user.is_authenticated:
        return redirect('blog:home')
    if request.method == 'POST' and 'user_id' in request.POST:
        user_id = request.POST['user_id']
        user = get_object_or_404(User, id=user_id)

        if not request.user.is_following(user):
            request.user.follow(user)
        else:
            request.user.unfollow(user)

        return redirect('blog:profile', username=username)

    try:
        user = User.objects.get(username=username)

        user_posts = Post.objects.filter(author=user)
        posts = [
            {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'author': post.author.username,
                'created_at': convert_post_created_date(post.created_at),
                'author_picture': convert_to_base_64(post.author),
                'image': convert_to_base_64(post),
                'comments': len(post.comments.all()),
                'claps': post.claps_count()
            } for post in user_posts
        ]
    except User.DoesNotExist:
        user = None
        posts = None

    return render(
        request,
        'blog/profile.html', {
            'user': user,
            'user_is_followed': request.user.is_following(user),
            'posts': posts,
            'picture': convert_to_base_64(request.user),
            'photo': convert_to_base_64(user)
        }
    )

def publish(request):
    if not request.user.is_authenticated:
        return redirect('blog:home')

    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']

        post = Post.objects.create(
            title=title,
            content=content,
            author=request.user,
            keywords=get_post_keywords(content)
        )

        if 'image' in request.FILES:
            post.picture = request.FILES['image'].read()
        else:
            default_image_path = Path(settings.BASE_DIR) / 'blog' / 'static' / 'blog' / 'images' / 'default-image.png'

            with open(default_image_path, 'rb') as f:
                post.picture = f.read()

        post.save()

        return redirect(reverse(
            'blog:view_post',
            kwargs={ 'username': request.user.username, 'post_id': post.id }
        ))

    return render(
        request,
        'blog/new_story.html',
        { 'user': request.user, 'picture': convert_to_base_64(request.user) }
    )

def view_post(request, username, post_id):
    if not request.user.is_authenticated:
        return redirect('blog:home')

    user_post = get_object_or_404(Post, id=post_id, author__username=username)

    for keyword in user_post.keywords:
        if keyword not in request.user.interests:
            request.user.interests.append(keyword)

    request.user.save()

    if request.method == 'POST':
        if 'user_id' in request.POST:
            user_id = request.POST['user_id']
            user = get_object_or_404(User, id=user_id)

            if not request.user.is_following(user):
                request.user.follow(user)
            else:
                request.user.unfollow(user)
        elif 'user_id_for_clap' in request.POST:
            if user_post.user_liked_post(request.user):
                user_post.unlike_post(request.user)
            else:
                user_post.like_post(request.user)
        elif 'comment' not in request.POST:
            user_post.delete()

            return redirect('blog:profile', username=username)
        else:
            comment = request.POST['comment']
            Comment.objects.create(content=comment, post=user_post, author=request.user)

        return redirect(reverse(
            'blog:view_post',
            kwargs={ 'username': username, 'post_id': post_id }
        ))

    post = {
        'id': user_post.id,
        'title': user_post.title,
        'content': user_post.content,
        'keywords': user_post.keywords,
        'created_at': user_post.created_at.date(),
        'author': user_post.author,
        'author_picture': convert_to_base_64(user_post.author),
        'image': convert_to_base_64(user_post),
        'author_is_followed': request.user.is_following(user_post.author),
        'claps': user_post.claps_count(),
        'user_liked': user_post.user_liked_post(request.user),
        'comments': {
            'amount': len(user_post.comments.all()),
            'responses': [
                {
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author.username,
                    'author_picture': convert_to_base_64(comment.author),
                    'created_at': comment.created_at.date()
                } for comment in user_post.comments.all()
            ]
        }
    }

    return render(
        request,
        'blog/view_post.html',
        { 'post': post, 'picture': convert_to_base_64(request.user), 'username': username }
    )

def user_update(request, username):
    if not request.user.is_authenticated:
        return redirect('blog:home')
    if request.user.username != username:
        return redirect('blog:profile', username=username)

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

        return redirect('blog:profile', username=username)

    return render(request, 'blog/user_update.html', {
        'user': request.user,
        'picture': convert_to_base_64(request.user)
    })

def post_update(request, username, post_id):
    if not request.user.is_authenticated:
        return redirect('blog:home')
    if request.user.username != username:
        return redirect('blog:profile', username=username)

    post = get_object_or_404(Post, id=post_id, author__username=username)

    if request.method == 'POST':
        post.title = request.POST['title']
        post.content = request.POST['content']

        if 'image' in request.FILES:
            post.picture = request.FILES['image'].read()
        else:
            default_image_path = Path(settings.BASE_DIR) / 'blog' / 'static' / 'blog' / 'images' / 'default-image.png'

            with open(default_image_path, 'rb') as f:
                post.picture = f.read()

        post.keywords = get_post_keywords(request.POST['content'])
        post.save()

        return redirect(reverse(
            'blog:view_post',
            kwargs={ 'username': request.user.username, 'post_id': post.id }
        ))

    return render(
        request,
        'blog/post_update.html',
        {
            'post': post,
            'picture': convert_to_base_64(request.user)
        }
    )
