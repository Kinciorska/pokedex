from django.contrib import auth

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse


class RegisterViewTestsCase(TestCase):
    def setUp(self) -> None:
        self.form_data = {'username': 'testuser',
                          'email': 'testuser@email.com',
                          'password1': 'FQ8fgxesdzUz',
                          'password2': 'FQ8fgxesdzUz'
                          }

    def test_register_page_url(self):
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='website/register.html')

    def test_register_page_view_name(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='website/register.html')

    def test_register_form_successful(self):
        response = self.client.post(reverse('register'), data=self.form_data)
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Registration successful.', messages)
        users = User.objects.all()
        self.assertEqual(users.count(), 1)

    def test_register_form_unsuccessful(self):
        self.form_data['password2'] = 'wrong_password'
        response = self.client.post(reverse('register'), data=self.form_data)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Unsuccessful registration - invalid information.', messages)
        self.assertEqual(response.status_code, 200)
        users = User.objects.all()
        self.assertEqual(users.count(), 0)

    def test_register_logging_in(self):
        self.client.post(reverse('register'), data=self.form_data)
        c = Client()
        logged_in = c.login(username='testuser', password='FQ8fgxesdzUz')
        self.assertTrue(logged_in)

class LoginViewTestsCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@email.com',
                                             password='FQ8fgxesdzUz'
                                             )
        self.form_data = {'username': 'testuser',
                          'password': 'FQ8fgxesdzUz'
                          }

    def test_login_page_url(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='website/login.html')

    def test_login_page_view_name(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='website/login.html')

    def test_login_logging_in(self):
        self.client.post(reverse('login'), data=self.form_data)
        c = Client()
        logged_in = c.login(username='testuser', password='FQ8fgxesdzUz')
        self.assertTrue(logged_in)

    def test_login_form_successful(self):
        response = self.client.post(reverse('login'), data=self.form_data)
        self.assertEqual(response.status_code, 302)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        username = self.form_data['username']
        self.assertIn(f'You are now logged in as {username}.', messages)

    def test_login_form_unsuccessful(self):
        self.form_data['password'] = 'wrong_password'
        response = self.client.post(reverse('login'), data=self.form_data)
        self.assertEqual(response.status_code, 200)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('Invalid username or password', messages)


class LogoutViewTestsCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@email.com',
                                             password='FQ8fgxesdzUz'
                                             )

        self.client.post(reverse('login'), data={'username': 'testuser',
                                                 'password': 'FQ8fgxesdzUz'
                                                 })

    def test_logout_page_url(self):
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 302)

    def test_logout_page_view_name(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_logout_logging_out(self):
        self.client.get(reverse('logout'))
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)
        response = self.client.get(reverse('logout'))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('You have successfully logged out.', messages)
