from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus
from ..forms import PostForm
from ..models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.create_user(username='Andrey')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group
        )


def test_create_group_post(self):
    """Создание поста группы"""
    posts_count = Post.objects.count()
    form_data = {
        'text': 'Пост группы',
        'group': self.group.id
    }
    response = self.authorized_client.post(
        reverse('posts:post_create'),
        data=form_data,
        follow=True
    )
    last_object = response.context['page_obj'][0]
    self.assertRedirects(response,
                         reverse('posts:profile',
                                 kwargs={'username': self.user.username}
                                 )
                         )
    self.assertEqual(Post.objects.count(), posts_count + 1)
    self.assertEqual(last_object.text, form_data['text'])
    self.assertEqual(last_object.group.id, form_data['group'])


def test_edit_group_post(self):
    """Редактирование поста с группой"""
    posts_count = Post.objects.count()
    form_data = {
        'text': 'Текст поста с группой',
        'group': self.group.id
    }
    response = self.authorized_client.post(
        reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        data=form_data,
        follow=True
    )
    post_context = response.context['post']
    self.assertRedirects(response,
                         reverse('posts:post_detail',
                                 kwargs={'post_id': self.post.id}
                                 )
                         )
    self.assertEqual(Post.objects.count(), posts_count)
    self.assertEqual(post_context.text, form_data['text'])
    self.assertEqual(post_context.group.id, form_data['group'])


def test_reddirect_guest_client(self):
    '''Проверка редиректа неавторизованного пользователя'''
    self.post = Post.objects.create(text='Тестовый текст',
                                    author=self.user,
                                    group=self.group
                                    )
    form_data = {'text': 'Текст записанный в форму'}
    response = self.guest_client.post(
        reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        data=form_data,
        follow=True
    )
    self.assertEqual(response.status_code, HTTPStatus.OK)
    self.assertRedirects(response,
                         f'/auth/login/?next=/posts/{self.post.id}/edit/'
                         )
