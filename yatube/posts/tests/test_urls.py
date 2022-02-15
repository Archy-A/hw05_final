from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.not_author = User.objects.create_user(username='not_author')

        cls.slug = 'test_group'
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись',
            group=cls.group,
            pub_date='01.01.2022'
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exist_for_any_user(self):
        """Страницы доступны любому пользователю."""
        templates_url_names = {
            HTTPStatus.OK: f'/posts/{self.post.id}/',
            HTTPStatus.OK: f'/profile/{self.user}/',
            HTTPStatus.OK: f'/group/{self.slug}/',
            HTTPStatus.OK: '/',
            HTTPStatus.NOT_FOUND: '/notexist/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, template)

    def test_urls_exist_for_auth_user(self):
        """Страницы доступны авториз. пользователю."""
        templates_url_names = {
            HTTPStatus.OK: '/create/',
            HTTPStatus.OK: f'/posts/{self.post.id}/edit/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, template)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        dic_create = 'create_post.html'
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_group/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'posts/create_post.html': '/create/',
            f'posts/{dic_create}': f'/posts/{self.post.id}/edit/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
