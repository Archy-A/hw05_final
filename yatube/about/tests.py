from django.contrib.auth import get_user_model
from django.test import Client, TestCase


User = get_user_model()

class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_about_url_exists_any_user(self):
        """ Cтраница об авторе доступна любому пользователю."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech_url_exists_any_user(self):
        """ Cтраница об технологиях доступна любому пользователю."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)