from django.test import TestCase
from .models import Post, Comment
from accounts.models import User
from .utils import *
from datetime import datetime, UTC, timedelta
from zoneinfo import ZoneInfo
from django.urls import reverse
from bs4 import BeautifulSoup
import base64

class MockImageObject:
    def __init__(self, picture):
        self.picture = picture

class UtilsTests(TestCase):
    def test_convert_to_base_64(self):
        mock_image_object = MockImageObject(b'this is a test image')

        expected_result = base64.b64encode(mock_image_object.picture).decode('utf-8')
        result = convert_to_base_64(mock_image_object)

        self.assertEqual(result, expected_result)

    def test_convert_post_created_date(self):
        date = datetime.now(UTC)
        self.assertEqual(convert_post_created_date(date), 'Few seconds ago')

        minutes_changed = date - timedelta(minutes=1)
        self.assertEqual(convert_post_created_date(minutes_changed), '1 minute(s) ago')

        hours_changed = date - timedelta(hours=1)
        self.assertEqual(convert_post_created_date(hours_changed), '1 hour(s) ago')

        days_changed = date - timedelta(days=1)
        self.assertEqual(convert_post_created_date(days_changed), '1 day(s) ago')

    def teste_create_post_object(self):
        user = User.objects.create_user(username='username', email='email@email.com', password='password')
        user.save()

        post = Post.objects.create(title='title', content='content', author=user)
        post.save()

        new_post = create_post_object(post)

        self.assertEqual(post.id, new_post['id'])
        self.assertEqual(post.title, new_post['title'])
        self.assertEqual(post.content, new_post['content'])
        self.assertEqual(post.author.username, new_post['author'])
        self.assertEqual(post.created_at.date(), new_post['created_at'])

class HomeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', email='email@email.com', password='password')
        self.user.save()

        self.user_login = self.client.login(username=self.user.username, password='password')
        self.assertTrue(self.user_login)

        self.response = self.client.get(reverse('blog:home'))

    def test_user_not_authenticated_redirection(self):
        response = self.client.get(reverse('accounts:logout'))

        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)
        self.assertRedirects(response, reverse('accounts:login'))

    def test_user_for_you_posts(self):
        self.user.interests = ['python']
        self.user.save()

        post = Post.objects.create(title='title', content='content', author=self.user, keywords=['python', 'django'])
        post.save()

        filtered_posts = [
            post for post in Post.objects.all()
            if any(keyword in self.user.interests for keyword in post.keywords)
        ]

        self.assertIn(post, filtered_posts)

    def test_user_following_posts(self):
        another_user = User.objects.create_user(username='another_username', email='email@email', password='password')
        another_user.save()
        self.user.follow(another_user)

        post = Post.objects.create(title='title', content='content', author=another_user)

        followed_users = [user for user in self.user.following.all()]
        filtered_posts = [
            post for post in Post.objects.filter(author__in=followed_users)
        ]

        self.assertIn(post, filtered_posts)

    def test_home_template(self):
        self.assertTemplateUsed(self.response, 'blog/home.html')

    def test_home_content(self):
        self.assertContains(self.response, 'Minium')
        self.assertContains(self.response, 'For you')
        self.assertContains(self.response, 'Following')
        self.assertContains(self.response, 'Nothing to show for now :(')

        soup = BeautifulSoup(self.response.content, 'html.parser')

        search_input = soup.find('input', attrs={ 'name': 'q' })
        self.assertIsNotNone(search_input)

class SearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', email='email@email.com', password='password')
        self.user.save()

        self.another_user = User.objects.create_user(username='another_username', email='email@e', password='password')
        self.another_user.save()

        self.post = Post.objects.create(title='java', content='script', author=self.another_user)
        self.post.save()

        self.user_login = self.client.login(username=self.user.username, password='password')
        self.assertTrue(self.user_login)

    def test_search_post(self):
        response = self.client.get(reverse('blog:search'), { 'q': self.post.title })
        self.assertContains(response, self.post.title)

    def test_search_user(self):
        response = self.client.get(reverse('blog:search_users'), { 'q': self.another_user.username })
        self.assertContains(response, self.another_user.username)

    def test_search_template(self):
        response = self.client.get(reverse('blog:search'), { 'q': 'python' })
        self.assertTemplateUsed(response, 'blog/search.html')

    def test_search_content(self):
        response = self.client.get(reverse('blog:search'), { 'q': 'python' })

        self.assertContains(response, 'Minium')
        self.assertContains(response, 'Stories')
        self.assertContains(response, 'People')
        self.assertContains(response, 'Results for')
        self.assertContains(response, 'Make sure all words are spelled correctly.')

class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', email='email@email.com', password='password')
        self.user.save()

        self.another_user = User.objects.create_user(username='another_username', email='email@e', password='password')
        self.another_user.save()

        self.user_login = self.client.login(username=self.user.username, password='password')
        self.assertTrue(self.user_login)

        self.response = self.client.get(reverse('blog:profile', kwargs={ 'username': self.user.username }))

    def test_user_posts(self):
        post = Post.objects.create(title='java', content='script', author=self.user)
        post.save()

        response = self.client.get(reverse('blog:profile', kwargs={ 'username': self.user.username }))

        self.assertContains(response, post.title)
        self.assertContains(response, convert_post_created_date(post.created_at))

    def test_follow_user(self):
        response = self.client.get(reverse('blog:profile', kwargs={ 'username': self.another_user.username }))

        self.assertContains(response, self.another_user.username)
        self.assertContains(response, 'Follow')

        response = self.client.post(reverse(
            'blog:profile',
            kwargs={'username': self.another_user.username}
        ), {'user_id': self.another_user.id})

        self.assertRedirects(response, reverse(
            'blog:profile', kwargs={'username': self.another_user.username}
        ))

    def test_logout(self):
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))

        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)

    def test_profile_template(self):
        self.assertTemplateUsed(self.response, 'blog/profile.html')

    def test_profile_content(self):
        self.assertContains(self.response, self.user.username)
        self.assertContains(self.response, self.user.email)
        self.assertContains(self.response, 'Without any bio yet.')
        self.assertContains(self.response, f'{self.user.username}\'s posts')
        self.assertContains(self.response, 'Edit profile')
        self.assertContains(self.response, 'Sign out')

class PublishTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', email='email@email.com', password='password')
        self.user.save()

        self.user_login = self.client.login(username=self.user.username, password='password')
        self.assertTrue(self.user_login)

        self.response = self.client.get(reverse('blog:new_story'))

    def test_publish_post(self):
        response = self.client.post(reverse('blog:new_story'), { 'title': 'java', 'content': 'script' })
        post = Post.objects.get(title='java', author=self.user)

        self.assertRedirects(response, reverse(
            'blog:view_post', kwargs={ 'username': self.user.username, 'post_id': post.id }
        ))

    def test_publish_template(self):
        self.client.login(username=self.user.username, password='password')

        response = self.client.get(reverse('blog:new_story'))
        self.assertTemplateUsed(response, 'blog/new_story.html')

    def test_publish_content(self):
        self.assertContains(self.response, 'Publish')

        soup = BeautifulSoup(self.response.content, 'html.parser')

        title_input = soup.find('input', attrs={ 'name': 'title' })
        self.assertIsNotNone(title_input)
        content_textarea = soup.find('textarea', attrs={ 'name': 'content' })
        self.assertIsNotNone(content_textarea)

class ViewPostTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', email='email@email.com', password='password')
        self.user.save()

        self.post = Post.objects.create(title='title', content='content', author=self.user)
        self.post.save()

        self.user_login = self.client.login(username=self.user.username, password='password')
        self.assertTrue(self.user_login)

        self.response = self.client.get(reverse('blog:view_post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))

    def test_clap_post(self):
        claps = self.post.claps_count()

        response = self.client.post(reverse(
            'blog:view_post', kwargs={ 'username': self.user.username, 'post_id': self.post.id }
        ), { 'user_id_for_clap': '' })

        self.assertRedirects(response, reverse(
            'blog:view_post', kwargs={ 'username': self.user.username, 'post_id': self.post.id }
        ))
        self.assertEqual(self.post.claps_count(), claps + 1)

    def test_delete_post(self):
        response = self.client.post(reverse(
            'blog:view_post', kwargs={ 'username': self.user.username, 'post_id': self.post.id }
        ))
        self.assertRedirects(response, reverse('blog:profile', kwargs={ 'username': self.user.username }))

    def test_comment_post(self):
        response = self.client.post(reverse(
            'blog:view_post', kwargs={ 'username': self.user.username, 'post_id': self.post.id }
        ), { 'comment': 'Nice post.' })

        self.assertRedirects(response, reverse(
            'blog:view_post', kwargs={ 'username': self.user.username, 'post_id': self.post.id }
        ))

        comment = Comment.objects.get(post=self.post)
        self.assertEqual(comment.content, 'Nice post.')

    def test_view_post_template(self):
        self.assertTemplateUsed(self.response, 'blog/view_post.html')

    def test_view_post_content(self):
        self.assertContains(self.response, self.user.username)
        self.assertContains(self.response, self.post.title)
        self.assertContains(self.response, self.post.content)
        self.assertContains(self.response, 'Responses (0)')
        self.assertContains(self.response, 'No comments yet')
        self.assertContains(self.response, 'Edit post')
        self.assertContains(self.response, 'Delete post')

class UserUpdateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', email='email@email.com', password='password')
        self.user.save()

        self.user_login = self.client.login(username=self.user.username, password='password')
        self.assertTrue(self.user_login)

        self.response = self.client.get(reverse('blog:update', kwargs={ 'username': self.user.username }))

    def test_user_update(self):
        self.client.post(reverse(
            'blog:update', kwargs={ 'username': self.user.username }
        ), { 'username': 'New username', 'bio': 'First bio' })

        user = User.objects.get(id=self.user.id)

        self.assertEqual(user.username, 'New username')
        self.assertEqual(user.bio, 'First bio')

    def test_user_update_template(self):
        self.assertTemplateUsed(self.response, 'blog/user_update.html')

    def test_user_update_content(self):
        self.assertContains(self.response, 'Profile information')
        self.assertContains(self.response, self.user.username)
        self.assertContains(self.response, 'Cancel')
        self.assertContains(self.response, 'Save')

class PostUpdateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', email='email@email.com', password='password')
        self.user.save()

        self.post = Post.objects.create(title='title', content='content', author=self.user)
        self.post.save()

        self.user_login = self.client.login(username=self.user.username, password='password')
        self.assertTrue(self.user_login)

        self.response = self.client.get(reverse('blog:post_update', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))

    def test_update_post(self):
        response = self.client.post(reverse(
            'blog:post_update', kwargs={ 'username': self.user.username, 'post_id': self.post.id }
        ), { 'title': 'New title', 'content': 'New content' })

        self.assertRedirects(response, reverse(
            'blog:view_post', kwargs={ 'username': self.user.username, 'post_id': self.post.id }
        ))

        post = Post.objects.get(id=self.post.id)

        self.assertEqual(post.title, 'New title')
        self.assertEqual(post.content, 'New content')

    def test_post_update_template(self):
        self.assertTemplateUsed(self.response, 'blog/post_update.html')

    def test_post_update_content(self):
        self.assertContains(self.response, 'Save and publish')

        soup = BeautifulSoup(self.response.content, 'html.parser')

        title_input = soup.find('input', attrs={ 'name': 'title' })
        self.assertIsNotNone(title_input)
        content_textarea = soup.find('textarea', attrs={ 'name': 'content' })
        self.assertIsNotNone(content_textarea)
