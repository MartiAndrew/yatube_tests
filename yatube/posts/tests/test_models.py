from django.test import TestCase
from ..models import Group, Post, User, NUM_SYMB


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Andrey')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_post_names(self):
        """Проверяем корректность работы __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:NUM_SYMB]
        self.assertEqual(expected_object_name, str(post))

    def test_models_have_correct_group_names(self):
        """Проверяем корректность работы __str__."""
        group = PostModelTest.group
        expected_group_name = group.title
        self.assertEqual(expected_group_name, str(group))

    def test_title_label(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_post_help_text(self):
        """Проверяем, help_text'ы у модели Post."""
        post = PostModelTest.post

        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }

        for field, expected_help_text in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_help_text
                )
