from django.test import TestCase
from django.urls import reverse


class HomePageTestsCase(TestCase):

    def test_home_page_url(self):
        response = self.client.get("/pokemons/home/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/home.html')

    def test_home_page_view_name(self):
        response = self.client.get(reverse('pokemons:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/home.html')
