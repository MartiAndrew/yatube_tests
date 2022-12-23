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
        group = PostsFormsTests.group
        test_post = Post.objects.create(
            text='Test post text',
            author=PostsFormsTests.author,
            group=group
        )
        test_post_id = test_post.id
        posts_count_before = Post.objects.count()

        new_group = Group.objects.create(
            title='Test group №2',
            description='another group for test',
            slug='test-2-slug'
        )
        form_data = {
            'text': 'Text with group',
            'group': new_group.id
        }
        response = self.auth_client.post(
            reverse('posts:post_edit', args={
                test_post.author.username, test_post.id}),
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.get(id=test_post_id)
        self.assertEqual(Post.objects.count(), posts_count_before)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group, new_group)
        self.assertEqual(edited_post.author, PostsFormsTests.user_author)
        self.assertEqual(response.status_code, HTTPStatus.OK)

