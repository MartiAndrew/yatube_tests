from http import HTTPStatus
from django.test import Client, TestCase
from django.core.cache import cache
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
        cls.index_url = '/'
        cls.group_url = f'/group/{PostURLTests.group.slug}/'
        cls.profile_url = f'/profile/{PostURLTests.author}/'
        cls.post_id_url = f'/posts/{PostURLTests.post.id}/'
        cls.edit_url = f'/posts/{PostURLTests.post.id}/edit/'
        cls.create = '/create/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        cache.clear()

    def test_urls_for_guests(self):
        """Страницы доступны любому пользователю."""
        field_url_names = {
            self.index_url: HTTPStatus.OK,
            self.group_url: HTTPStatus.OK,
            self.profile_url: HTTPStatus.OK,
            self.post_id_url: HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for value, expected in field_url_names.items():
            with self.subTest(value=value):
                response = self.client.get(value).status_code
                self.assertEqual(response, expected)

    def test_urls_posts_template(self):
        """Проверка, что URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            self.index_url: 'posts/index.html',
            self.group_url: 'posts/group_list.html',
            self.profile_url: 'posts/profile.html',
            self.post_id_url: 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_edit_url_uses_correct_template(self):
        """Страница /edit/ использует шаблон create_post.html """
        response = self.authorized_client.get(self.edit_url)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_url_exists_at_desired_location(self):
        """Проверка, что создание доступно авторизованному пользователю."""
        response = self.authorized_client.get(self.create)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_exists_at_desired_location(self):
        """Проверка, что редакт-е доступно авторизованному пользователю."""
        response = self.authorized_client.get(self.edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous(self):
        """Тест о редиректе неавторизованного юзера со страницы /create/."""
        response = self.guest_client.get(self.create)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_edit_url_redirect_anonymous(self):
        """Тест о редиректе неавторизованного юзера со страницы /edit/."""
        response = self.guest_client.get(self.edit_url)
        self.assertRedirects(
            response,
            (f'/auth/login/?next=/posts/{PostURLTests.post.id}/edit/')
        )
