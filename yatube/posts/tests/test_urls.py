from http import HTTPStatus
from django.test import Client, TestCase
from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Andrey')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test-description',
        )
        cls.post = Post.objects.create(
            text='test_post_text',
            author=cls.author
        )
        cls.field_url_names = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{PostURLTests.author}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.id}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_urls_for_guests(self):
        """Страницы доступны любому пользователю."""

        for value, expected in self.field_url_names.items():
            with self.subTest(value=value):
                response = self.client.get(value).status_code
                self.assertEqual(response, expected)

    def test_urls_posts_template(self):
        """Проверка, что URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.author}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_edit_url_uses_correct_template(self):
        """Страница /edit/ использует шаблон create_post.html """
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_url_exists_at_desired_location(self):
        """Проверка, что создание доступно авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_exists_at_desired_location(self):
        """Проверка, что редакт-е доступно авторизованному пользователю."""
        response = self.authorized_client.get(
            f'/posts/{PostURLTests.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous(self):
        """Тест о редиректе неавторизованного юзера со страницы /create/."""
        response = self.guest_client.get('/create/')
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_edit_url_redirect_anonymous(self):
        """Тест о редиректе неавторизованного юзера со страницы /edit/."""
        response = self.guest_client.get(
            f'/posts/{PostURLTests.post.id}/edit/'
        )
        self.assertRedirects(
            response,
            (f'/auth/login/?next=/posts/{PostURLTests.post.id}/edit/')
        )
