from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus
from ..models import Group, Post, User


class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Andrey')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test-description',
        )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(PostsFormsTests.author)

    def test_create_group_post(self):
        """Создание поста"""
        form_data = {
            'text': 'Пост группы',
            'group': self.group.id
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        last_object = Post.objects.last()
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(last_object.text, form_data['text'])
        self.assertEqual(last_object.group.id, form_data['group'])
        self.assertEqual(last_object.author, self.author)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_group_post(self):
        """Редактирование поста"""
        post = Post.objects.create(text='Тестовый текст',
                                        author=self.author,
                                        group=self.group
                                        )
        new_group = Group.objects.create(title='Тестовая группа2',
                                           slug='test-group',
                                           description='Описание'
                                           )
        form_data = {'text': 'Текст записанный в форму',
                     'group': new_group.id}
        response = self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.get(id=post.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.id, form_data['group'])
        self.assertEqual(edited_post.author, post.author)
        self.assertEqual(self.group.posts.count(), 0)
        self.assertEqual(Post.objects.count(), 1)
