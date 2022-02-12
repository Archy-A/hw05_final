from django.contrib.auth import get_user_model
from django.test import Client, TestCase

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
        self.user = PostURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_author = PostURLTests.not_author
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.not_author)

    def test_about_url_exists_any_user(self):
        """ Cтраница об авторе доступна любому пользователю."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech_url_exists_any_user(self):
        """ Cтраница об технологиях доступна любому пользователю."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_home_url_exists_any_user(self):
        """Главная страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url_exist_any_user(self):
        """Страница /group/<slug> ГРУППА доступна любому пользователю."""
        response = self.guest_client.get(f'/group/{PostURLTests.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exist_any_user(self):
        """Страница /profile/<username> ПРОФИЛЬ доступна
        любому пользователю."""
        response = self.guest_client.get(f'/profile/{PostURLTests.user}/')
        self.assertEqual(response.status_code, 200)

    def test_post_url_exist_any_user(self):
        """Страница /posts/<post_id> ПОСТ доступна любому пользователю."""
        response = self.guest_client.get(f'/posts/{PostURLTests.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_url_unexist_any_user(self):
        """Страница 404 для любого пользователя."""
        response = self.guest_client.get('/notexist/')
        self.assertEqual(response.status_code, 404)

    def test_create_post_url_exist_auth_user(self):
        """Страница /create/<post_id> СОЗДАТЬ ПОСТ
        доступна авториз.пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exist_auth_user(self):
        """Страница /posts/<post_id>/edit/ РЕД.ПОСТ доступна
        авториз.пользователю."""
        response = self.authorized_client.get(
            f'/posts/{PostURLTests.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        dic_create = 'create_post.html'
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_group/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': f'/posts/{PostURLTests.post.id}/',
            'posts/create_post.html': '/create/',
            f'posts/{dic_create}': f'/posts/{PostURLTests.post.id}/edit/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
