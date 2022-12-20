from django.test import TestCase
from ..models import Group, Post, User

NUM_SYMB = 15


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
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )
