from django.test import TestCase
from django.urls import reverse
from accounts.models import User

class LandingPageTests(TestCase):
    def test_landing_index(self):
        response = self.client.get(reverse('landing:landing'))

        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_redirection(self):
        user = User.objects.create_user(username='user', email='email@email.com', password='password')
        user.save()

        user_login = self.client.login(username='user', password='password')
        self.assertTrue(user_login)

        response = self.client.get(reverse('landing:landing'))
        self.assertRedirects(response, reverse('blog:home'))
        self.assertEqual(response.status_code, 302)

    def test_landing_page_template(self):
        response = self.client.get(reverse('landing:landing'))
        self.assertTemplateUsed(response, 'landing/landing_page.html')

    def test_landing_page_content(self):
        response = self.client.get(reverse('landing:landing'))

        self.assertContains(response, 'Get started')
        self.assertContains(response, 'Sign in')
        self.assertContains(response, 'Start reading')
