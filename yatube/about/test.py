from django.test import Client, TestCase
from http import HTTPStatus


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exists_at_desired_locations(self):
        """Проверяем доступность страниц по URL приложения About."""

        field_url_names = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for value, expected in field_url_names.items():
            with self.subTest(value=value):
                response = self.client.get(value).status_code
                self.assertEqual(response, expected)

    def test_about_urls_uses_correct_template(self):
        """Проверяем шаблоны страниц приложения About."""

        url_templates_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
