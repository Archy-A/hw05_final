from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group
from django.core.cache import cache
from yatube.settings import POSTS_NUMBER, ONE_RECORD, TEN_RECORDS

User = get_user_model()


class PostVIEWTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.not_author = User.objects.create_user(username="not_author")

        cls.slug = "test_group_29"
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_group_29",
            description="Тестовое описание",
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.not_author)

    def test_index_first_page_cache_contains_records(self):
        """Тест на кэш контекст"""
        response_one = self.guest_client.get(reverse("posts:index"))
        response_one_obj_con = response_one.context["page_obj"][0].id
        form_data = {
            "text": "Тестовый пост",
        }
        self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        response_two = self.guest_client.get(reverse("posts:index"))
        response_two_obj_con = response_two.context["page_obj"][0].id
        self.assertEqual(response_one_obj_con, response_two_obj_con)
        cache.clear()
        response_three = self.guest_client.get(reverse("posts:index"))
        response_three_obj_con = response_three.context["page_obj"][0].id
        self.assertNotEqual(response_two_obj_con, response_three_obj_con)
        cache.clear()

    def test_index_first_page_cache_contains_records(self):
        """Тест на кэш контент"""
        response_one = self.guest_client.get(reverse("posts:index"))
        response_one_obj_con = response_one.content
        form_data = {
            "text": "Тестовый пост",
        }
        self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        response_two = self.guest_client.get(reverse("posts:index"))
        response_two_obj_con = response_two.content
        self.assertEqual(response_one_obj_con, response_two_obj_con)
        cache.clear()
        response_three = self.guest_client.get(reverse("posts:index"))
        response_three_obj_con = response_three.content
        self.assertNotEqual(response_two_obj_con, response_three_obj_con)
