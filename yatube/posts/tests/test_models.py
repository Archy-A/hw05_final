from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_str_post(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected = post.text[:15]
        self.assertEqual(str(post), expected)

    def test_models_str_group(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        expected = group.title
        self.assertEqual(str(group), expected)
