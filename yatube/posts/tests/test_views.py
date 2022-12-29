from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from posts.models import Group, Post, User

PAGE_1_POSTS = 10


# Леш, здравствуй. Решил сделать кэш через view-функцию. Не знаю насколько правильно,
# Возникли проблемы с тестами, с добавлением cache.clear(). В пачке писали, что если
# через шаблон кэш реализовывать, то нет этой проблемы. Не совсем понял, почему так?
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Andrey')
        cls.group_1 = Group.objects.create(
            title='test_group_title_1',
            slug='test_slug_1',
            description='test_description_1',
        )
        cls.group_2 = Group.objects.create(
            title='test_group_title_2',
            slug='test_slug_2',
            description='test_description_2',
        )
        cls.post = Post.objects.create(
            text='test_text',
            pub_date='test_date',
            author=cls.author,
            group=cls.group_1,
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.author)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """Проверка какие вызываются шаблоны, при вызове вьюхи через name"""
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list', kwargs={
                'slug': PostViewTests.group_1.slug}
                                             ),
            'posts/profile.html': reverse('posts:profile', kwargs={
                'username': PostViewTests.author.username}
                                          ),
            'posts/post_detail.html': reverse('posts:post_detail', kwargs={
                'post_id': PostViewTests.post.id}
                                              ),
            'posts/create_post.html': reverse('posts:post_edit', kwargs={
                'post_id': PostViewTests.post.id}
                                              ),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.auth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse('posts:index'))
        context = response.context['page_obj'][0]
        self.assertEqual(context.text, 'test_text')
        self.assertEqual(context.author, self.author)
        self.assertEqual(context.group, self.group_1)
        self.assertEqual(context.image, self.post.image)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:group_list', kwargs={
            'slug': PostViewTests.group_1.slug}
                                                 )
                                         )
        context = response.context['page_obj'][0]
        self.assertEqual(context.text, 'test_text')
        self.assertEqual(context.group, self.group_1)
        self.assertEqual(context.image, self.post.image)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse('posts:profile', kwargs={
            'username': PostViewTests.author.username}
                                                )
                                        )
        context = response.context['page_obj'][0]
        context_posts_count = response.context['posts_count']
        self.assertEqual(context.text, self.post.text)
        self.assertEqual(context.author, self.author)
        self.assertEqual(context_posts_count, Post.objects.count())
        self.assertEqual(context.image, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.auth_client.get(
            reverse('posts:post_detail', kwargs={
                'post_id': PostViewTests.post.id}
                    )
        )
        self.assertEqual(
            response.context['post_item'].text, 'test_text'
        )
        self.assertEqual(
            response.context['post_item'].image, self.post.image
        )

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': PostViewTests.post.id}
        )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_is_on_pages(self):
        """Проверка, что созданный пост появляется на нужных страницах."""
        response_index = self.auth_client.get(reverse('posts:index'))
        response_group_list = self.auth_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': PostViewTests.group_1.slug}
        )
        )
        response_profile = self.auth_client.get(reverse(
            'posts:profile',
            kwargs={'username': PostViewTests.author.username}
        )
        )
        for response in [response_index,
                         response_group_list, response_profile]:
            context = response.context['page_obj'][0]
            with self.subTest():
                self.assertTrue(PostViewTests.post
                                in response.context['page_obj']
                                )
                self.assertEqual(context.text, PostViewTests.post.text)
                self.assertEqual(context.author, PostViewTests.author)
                self.assertEqual(context.group, PostViewTests.group_1)

    def test_post_in_right_group(self):
        """Проверка, что этот пост не попал в группу,
        для которой не был предназначен."""
        response = self.auth_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': PostViewTests.group_2.slug}
        )
        )
        self.assertTrue(PostViewTests.post
                        not in response.context['page_obj']
                        )

    def test_cache_index_page(self):
        """Проверка работы кеша"""
        post = Post.objects.create(
            text='Пост для кеширования',
            author=self.author)
        post_text_add = self.auth_client.get(
            reverse('posts:index')).content
        post.delete()
        post_text_delete = self.auth_client.get(
            reverse('posts:index')).content
        self.assertEqual(post_text_add, post_text_delete)
        cache.clear()
        post_text_cache_clear = self.auth_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(post_text_add, post_text_cache_clear)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page_obj = []
        cls.author = User.objects.create_user(username='Andrey')
        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_slug',
            description='test_description',
        )
        cls.guest_client = Client()
        batch = (Post(
            author=cls.author,
            text=f'Test {i}',
            group=cls.group
        ) for i in range(13))
        cls.posts = Post.objects.bulk_create(batch)
        cache.clear()

    def test_posts_pages_correct_paginator_work(self):
        """Проверка паджинатора на нужных страницах"""
        urls_names_2page = {
            reverse('posts:index'): 3,
            reverse('posts:group_list', kwargs={
                'slug': PaginatorViewsTest.group.slug}
                    ): 3,
            reverse('posts:profile', kwargs={
                'username': PaginatorViewsTest.author.username}
                    ): 3,
        }

        for page, page_2_posts in urls_names_2page.items():
            with self.subTest(page=page):
                response_page_1 = self.guest_client.get(page)
                response_page_2 = self.guest_client.get(page + '?page=2')

                self.assertEqual(
                    len(response_page_1.context['page_obj']),
                    PAGE_1_POSTS
                )
                self.assertEqual(
                    len(response_page_2.context['page_obj']),
                    page_2_posts
                )
