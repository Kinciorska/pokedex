from django.contrib.auth.models import User
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

        users = User.objects.all()
        self.assertEqual(users.count(), 1)

    def test_register_form_unsuccessful(self):
        self.form_data['password2'] = 'wrong_password'
        response = self.client.post(reverse('register'), data=self.form_data)
        self.assertEqual(response.status_code, 200)

        users = User.objects.all()
        self.assertEqual(users.count(), 0)

    def test_register_logging_in(self):
        self.client.post(reverse('register'), data=self.form_data)
        c = Client()
        logged_in = c.login(username='testuser', password='FQ8fgxesdzUz')
        self.assertTrue(logged_in)
