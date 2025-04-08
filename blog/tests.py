from bs4 import BeautifulSoup
from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from .models import Post, Comment

class HomePageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', email='email@email.com', password='password')
        self.user.save()

        self.user_login = self.client.login(username=self.user.username, password='password')
        self.response = self.client.get(reverse('blog:home'))

    def test_user_following_posts(self):
        second_user = User.objects.create_user(username='second', email='second@email.com', password='password')
        second_user.save()

        self.user.follow(second_user)
        second_user_post = Post.objects.create(title='post', story='post content', author=second_user)

        followed_users = [user for user in self.user.following.all()]
        filtered_posts = [post for post in Post.objects.filter(author__in=followed_users)]

        self.assertIn(second_user_post, filtered_posts)

    def test_home_page_template(self):
        self.assertTemplateUsed(self.response, 'blog/home_page.html')

    def test_home_page_content(self):
        soup = BeautifulSoup(self.response.content.decode('utf-8'), 'html.parser')

        search_input = soup.find('input', attrs={ 'name': 'q' })

        self.assertIsNotNone(search_input)
        self.assertContains(self.response, 'Minium')
        self.assertContains(self.response, 'For you')
        self.assertContains(self.response, 'Following')

class SearchPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', email='email@email.com', password='password')
        self.user.save()

        self.second_user = User.objects.create_user(username='second', email='second@email.com', password='password')
        self.second_user.save()

        self.post = Post.objects.create(title='post', story='post content', author=self.second_user)
        self.post.save()

        self.user_login = self.client.login(username=self.user.username, password='password')

    def test_search_post(self):
        response = self.client.get(reverse('blog:search_posts'), { 'q': self.post.title })
        self.assertContains(response, self.post.title)

    def test_search_user(self):
        response = self.client.get(reverse('blog:search_posts'), { 'q': self.second_user.username })
        self.assertContains(response, self.second_user.username)

    def test_search_page_template(self):
        response = self.client.get(reverse('blog:search_posts'), { 'q': 'java' })
        self.assertTemplateUsed(response, 'blog/search_page.html')

    def test_search_page_content(self):
        response = self.client.get(reverse('blog:search_posts'), { 'q': 'java' })

        self.assertContains(response, 'Minium')
        self.assertContains(response, 'Stories')
        self.assertContains(response, 'People')
        self.assertContains(response, 'java')

class NewStoryPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', email='email@email.com', password='password')
        self.user.save()

        self.user_login = self.client.login(username=self.user.username, password='password')
        self.response = self.client.get(reverse('blog:new_story'))

    def test_publish_post(self):
        response = self.client.post(reverse('blog:new_story'), {
            'title': 'java',
            'story': 'script'
        })
        post = Post.objects.get(title='java')

        self.assertRedirects(response, reverse('blog:view_post', kwargs={
            'username': self.user.username, 'post_id': post.id
        }))

    def test_new_story_page_template(self):
        self.assertTemplateUsed(self.response, 'blog/new_story_page.html')

    def test_new_story_page_content(self):
        soup = BeautifulSoup(self.response.content.decode('utf-8'), 'html.parser')

        title_input = soup.find('input', attrs={ 'name': 'title' })
        story_textarea = soup.find('textarea', attrs={ 'name': 'story' })

        self.assertIsNotNone(title_input)
        self.assertIsNotNone(story_textarea)
        self.assertContains(self.response, 'Publish')

class ViewPostPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', email='email@email.com', password='password')
        self.user.save()

        self.post = Post.objects.create(title='post', story='post content', author=self.user)
        self.post.save()

        self.user_login = self.client.login(username=self.user.username, password='password')
        self.response = self.client.get(reverse('blog:view_post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))

    def test_comment_post(self):
        response = self.client.post(reverse('blog:view_post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }), { 'comment': 'nice post' })

        self.assertRedirects(response, reverse('blog:view_post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))

        comment = Comment.objects.get(post=self.post)
        self.assertEqual(comment.content, 'nice post')

    def test_view_post_page_template(self):
        self.assertTemplateUsed(self.response, 'blog/view_post_page.html')

    def test_view_post_page_content(self):
        self.assertContains(self.response, self.user.username)
        self.assertContains(self.response, self.post.title)
        self.assertContains(self.response, self.post.story)
        self.assertContains(self.response, 'Responses (0)')
        self.assertContains(self.response, 'No comments yet')

class ProfilePageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', email='email@email.com', password='password')
        self.user.save()

        self.user_login = self.client.login(username=self.user.username, password='password')
        self.response = self.client.get(reverse('blog:profile', kwargs={ 'username': self.user.username }))

    def test_user_posts(self):
        post = Post.objects.create(title='post', story='post content', author=self.user)
        post.save()

        self.assertContains(self.response, post.title)

    def test_logout(self):
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))

        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)

    def test_profile_page_template(self):
        self.assertTemplateUsed(self.response, 'blog/profile_page.html')

    def test_profile_page_content(self):
        self.assertContains(self.response, self.user.username)
        self.assertContains(self.response, 'Without any bio yet.')
        self.assertContains(self.response, f'{self.user.username}\'s posts')

class UpdateUserPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', email='email@email.com', password='password')
        self.user.save()

        self.user_login = self.client.login(username=self.user.username, password='password')
        self.response = self.client.get(reverse('blog:update_user', kwargs={ 'username': self.user.username }))

    def test_update_user(self):
        self.client.post(reverse('blog:update_user', kwargs={ 'username': self.user.username }), {
            'bio': 'first bio'
        })

        user = User.objects.get(username=self.user.username)
        self.assertEqual(user.bio, 'first bio')

    def test_update_user_page_template(self):
        self.assertTemplateUsed(self.response, 'blog/update_user_page.html')

    def test_update_user_page_content(self):
        soup = BeautifulSoup(self.response.content.decode('utf-8'), 'html.parser')

        bio_textarea = soup.find('textarea', attrs={ 'name': 'bio' })

        self.assertIsNotNone(bio_textarea)
        self.assertContains(self.response, 'Profile information')

class UpdatePostPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', email='email@email.com', password='password')
        self.user.save()

        self.post = Post.objects.create(title='post', story='post content', author=self.user)
        self.post.save()

        self.user_login = self.client.login(username=self.user.username, password='password')
        self.response = self.client.get(reverse('blog:update_post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))

    def test_update_post(self):
        response = self.client.post(reverse('blog:update_post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }), { 'title': 'new title', 'story': 'new story' })
        self.assertRedirects(response, reverse('blog:view_post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))

        post = Post.objects.get(id=self.post.id)

        self.assertEqual(post.title, 'new title')
        self.assertEqual(post.story, 'new story')

    def test_update_post_page_template(self):
        self.assertTemplateUsed(self.response, 'blog/new_story_page.html')

    def test_update_post_page_content(self):
        self.assertContains(self.response, 'Update')
        self.assertContains(self.response, self.post.title)
        self.assertContains(self.response, self.post.story)

class DeletePostTests(TestCase):
    def test_delete_post(self):
        user = User.objects.create_user(username='user', email='email@email.com', password='password')
        user.save()

        post = Post.objects.create(title='post', story='post content', author=user)
        post.save()

        post_id = post.id

        self.client.login(username=user.username, password='password')
        self.client.post(reverse('blog:delete_post', kwargs={
            'username': user.username,
            'post_id': post.id
        }))

        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(id=post_id)

class LikeOrUnlikePostTests(TestCase):
    def test_like_or_unlike_post(self):
        user = User.objects.create_user(username='user', email='email@email.com', password='password')
        user.save()

        second_user = User.objects.create_user(username='second', email='second@email.com', password='password')
        second_user.save()

        post = Post.objects.create(title='post', story='post content', author=second_user)
        post.save()

        post_likes = post.claps_amount()

        post.like_post(user)
        self.assertEqual(post.claps_amount(), post_likes + 1)

        post.unlike_post(user)
        self.assertEqual(post.claps_amount(), post_likes)
