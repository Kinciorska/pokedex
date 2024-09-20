from django.test import TestCase

from website.forms import NewUserForm

class NewUserTestsCase(TestCase):
    def setUp(self) -> None:
        self.form_data = {'username': 'testuser',
                          'email': 'testuser@email.com',
                          'password1': 'FQ8fgxesdzUz',
                          'password2': 'FQ8fgxesdzUz'
                          }

    def test_user_data_form_valid(self):
        form = NewUserForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_user_data_form_invalid(self):
        self.form_data['password2'] = 'wrong_password'
        form = NewUserForm(data=self.form_data)
        self.assertFalse(form.is_valid())
