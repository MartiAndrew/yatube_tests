import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus
from ..models import Group, Post, Comment, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Andrey')
        cls.comm_author = User.objects.create_user(
            username='commentator')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test-description',
        )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(PostsFormsTests.author)
        self.auth_user_comm = Client()
        self.auth_user_comm.force_login(self.comm_author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_auth_user_create_comment(self):
        """Cоздание комментария авторизированным клиентом."""
        post = Post.objects.create(
            text='Текст поста для комментирования',
            author=self.author)
        form_data = {'text': 'Тестовый комментарий'}
        response = self.auth_user_comm.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.last()
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.comm_author)
        self.assertEqual(comment.post_id, post.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_group_post(self):
        """Создание поста в базе данных"""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Пост группы',
            'group': self.group.id,
            'image': uploaded
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
        self.assertEqual(last_object.image.name, 'posts/small.gif')
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



