from django.test import TestCase
from django.urls import reverse
from .models import User
from bs4 import BeautifulSoup

class UserLoginTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='user', email='email@email.com', password='password')
        user.save()

    def test_authenticated_user_redirection(self):
        user_login = self.client.login(username='user', password='password')
        self.assertTrue(user_login)

        response = self.client.get(reverse('accounts:login'))
        self.assertRedirects(response, reverse('blog:home'))
        self.assertEqual(response.status_code, 302)

    def test_login_success(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'user', 'password': 'password'
        })
        self.assertRedirects(response, reverse('blog:home'))

    def test_user_login_template(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertTemplateUsed(response, 'accounts/login_page.html')

    def test_user_login_page_content(self):
        response = self.client.get(reverse('accounts:login'))
        soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')

        username_input = soup.find('input', attrs={ 'name': 'username' })
        password_input = soup.find('input', attrs={ 'name': 'password' })

        self.assertIsNotNone(username_input)
        self.assertIsNotNone(password_input)
        self.assertContains(response, 'Sign in')
        self.assertContains(response, 'Create one')

class UserLogoutTests(TestCase):
    def test_user_logout_success(self):
        user = User.objects.create_user(username='user', email='email@email.com', password='password')
        user.save()

        user_login = self.client.login(username='user', password='password')
        self.assertTrue(user_login)

        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))

        user = self.client.session.get('_user_user_id')
        self.assertIsNone(user)

class UserRegisterTests(TestCase):
    def test_user_register_success(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'username',
            'password': 'password',
            'email': 'email@email.com',
            'month': '12',
            'day': '27',
            'year': '2000'
        })

        self.assertRedirects(response, reverse('blog:home'))

    def test_register_page_template(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertTemplateUsed(response, 'accounts/register_page.html')

    def test_register_page_content(self):
        response = self.client.get(reverse('accounts:register'))
        soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')

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
