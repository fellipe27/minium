from django.test import TestCase
from .models import User
from django.urls import reverse
from bs4 import BeautifulSoup
from django.contrib.messages import get_messages
import datetime

class UserLoginTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='username', email='email@email.com', password='password')
        user.save()

    def test_authenticated_user_redirection(self):
        user_login = self.client.login(username='username', password='password')
        self.assertTrue(user_login)

        response = self.client.get(reverse('accounts:login'))
        self.assertRedirects(response, reverse('blog:home'))
        self.assertEqual(response.status_code, 302)

    def test_login_success(self):
        response = self.client.post(reverse('accounts:login'), { 'username': 'username', 'password': 'password' })

        self.assertRedirects(response, reverse('blog:home'))

    def test_login_failure(self):
        response = self.client.post(reverse('accounts:login'), { 'username': 'username', 'password': 'wrong' })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User not found.')

    def test_user_login_template(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_user_login_content(self):
        response = self.client.get(reverse('accounts:login'))
        soup = BeautifulSoup(response.content, 'html.parser')

        username_input = soup.find('input', attrs={ 'name': 'username' })
        password_input = soup.find('input', attrs={ 'name': 'password' })

        self.assertIsNotNone(username_input)
        self.assertIsNotNone(password_input)
        self.assertContains(response, 'Sign in')
        self.assertContains(response, 'Create one')

    def test_signup_redirection(self):
        self.client.get(reverse('accounts:login'))
        response = self.client.get(reverse('accounts:register'))

        self.assertEqual(response.status_code, 200)

class UserLogoutTests(TestCase):
    def test_user_logout_success(self):
        user = User.objects.create_user(username='username', email='email@email.com', password='password')
        user.save()

        user_login = self.client.login(username='username', password='password')
        self.assertTrue(user_login)

        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))

        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)

class UserRegisterTests(TestCase):
    def test_user_register_success(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'username',
            'password': 'password' ,
            'email': 'email@email.com',
            'month': '12',
            'day': '27',
            'year': '2000'
        })

        self.assertRedirects(response, reverse('blog:home'))

    def test_user_register_with_invalid_birthday(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'username',
            'password': 'password',
            'email': 'email@email.com',
            'month': '120',
            'day': '277',
            'year': '20000'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid birthday.')

    def test_user_register_with_existing_data(self):
        old_user = User.objects.create_user(username='username', email='email@email.com', password='password')
        old_user.save()

        response = self.client.post(reverse('accounts:register'), {
            'username': 'username',
            'password': 'password',
            'email': 'email@email.com',
            'month': '12',
            'day': '27',
            'year': '2000'
        })

        self.assertRedirects(response, reverse('accounts:register'))

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('User already exists.' in str(message) for message in messages))

    def test_user_login_template(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_user_login_content(self):
        response = self.client.get(reverse('accounts:register'))
        soup = BeautifulSoup(response.content, 'html.parser')

        email_input = soup.find('input', attrs={ 'name': 'email' })
        username_input = soup.find('input', attrs={ 'name': 'username' })
        password_input = soup.find('input', attrs={ 'name': 'password' })
        month_input = soup.find('input', attrs={ 'name': 'month' })
        day_input = soup.find('input', attrs={ 'name': 'day' })
        year_input = soup.find('input', attrs={ 'name': 'year' })

        self.assertIsNotNone(email_input)
        self.assertIsNotNone(username_input)
        self.assertIsNotNone(password_input)
        self.assertIsNotNone(month_input)
        self.assertIsNotNone(day_input)
        self.assertIsNotNone(year_input)

        self.assertContains(response, 'Sign up')
        self.assertContains(response, 'Sign in')
