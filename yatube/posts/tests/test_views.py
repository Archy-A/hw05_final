from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from ..models import Group, Post
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

        cls.post = Post.objects.create(
            author=cls.user, text="Тестовая запись", group=cls.group
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.not_author)      

    def test_uses_correct_template(self):
        post = Post.objects.get(id=1)
        views_template = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": f"{post.group.slug}"}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": f"{self.user}"}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": f"{post.id}"}
            ): "posts/post_detail.html",
            reverse("posts:post_create"): "posts/create_post.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": f"{post.id}"}
            ): "posts/create_post.html",
        }
        for address, template in views_template.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_context_post_detail(self):
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": f"{self.post.id}"})
        )
        post = response.context.get("post")
        context_fields = {
            post.text: f"{self.post.text}",
            post.author.username: f"{self.user.username}",
            post.group.title: f"{self.group.title}",
            post.group.description: f"{self.group.description}",
            post.group.slug: f"{self.group.slug}",
        }
        for value, expected in context_fields.items():
            self.assertEqual(value, expected)

    def context_function(self, response):
        post = response.context["page_obj"][0]
        context_fields = {
            "id": post.id,
            "text": post.text,
            "pub_date": post.pub_date,
            "author": post.author,
        }
        for value in context_fields.values():
            return self.assertIsNotNone(value)

    def test_context_index(self):
        response = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(len(response.context.get("page_obj").object_list), 1)
        self.assertTrue(len(response.context.get("page_obj").object_list) > 0)
        self.context_function(response)
        cont = response.context
        context_fields = {
            cont["page_obj"][0].text: "Тестовая запись",
        }
        for value, expected in context_fields.items():
            self.assertEqual(value, expected)

    def test_context_grouplist(self):
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "test_group_29"})
        )
        self.context_function(response)
        cont = response.context
        context_fields = {
            cont["group"].title: "Тестовая группа",
            cont["page_obj"][0].text: "Тестовая запись",
        }
        for value, expected in context_fields.items():
            self.assertEqual(value, expected)

    def test_context_profile(self):
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": "auth"})
        )
        self.context_function(response)
        cont = response.context
        context_fields = {
            cont["user"].username: "auth",
            cont["page_obj"][0].text: "Тестовая запись",
            cont["post_count"]: 1,
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_context_post_create(self):
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "group": forms.models.ModelChoiceField,
            "text": forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)
        get_form = response.context.get("form")
        self.assertIsInstance(get_form, PostForm)
        self.assertFalse(response.context["is_edit"])

    def test_context_post_edit(self):
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": f"{self.post.id}"})
        )
        form_fields = {
            "group": forms.models.ModelChoiceField,
            "text": forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_in_url(self):
        response = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(self.post, response.context["page_obj"][0])

    def test_post_not_in_group2(self):
        self.group = Group.objects.create(
            title="Тестовая группа 33",
            slug="test_group_33",
            description="Тестовое описание 33",
        )
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "test_group_33"})
        )
        self.assertNotIn(self.post, response.context.get("page_obj"))


class PaginatorVIEWTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="user")
        cls.slug = "test_group"
        cls.group = Group.objects.create(
            title="Тестовая группа", slug="test_group",
            description="Тестовое описание"
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = self.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post = (
            Post(author=self.user, text=f"Тест {i}", group=self.group)
            for i in range(POSTS_NUMBER)
        )
        Post.objects.bulk_create(self.post)

    def test_pages_contain_ten_records(self):
        cache.clear()
        context_fields = {
            self.client.get(reverse("posts:index")): TEN_RECORDS,
            self.client.get(
                reverse("posts:group_list", kwargs={"slug": f"{self.slug}"})
            ): TEN_RECORDS,
            self.client.get(
                reverse("posts:profile", kwargs={"username": f"{self.user}"})
            ): TEN_RECORDS,
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                cache.clear()
                self.assertEqual(len(value.context["page_obj"]), expected)

    def test_pages_contain_one_record(self):
        context_fields = {
            self.client.get(reverse("posts:index") + "?page=2"): ONE_RECORD,
            self.client.get(
                reverse("posts:group_list", kwargs={"slug": f"{self.slug}"})
                + "?page=2"
            ): ONE_RECORD,
            self.client.get(
                reverse("posts:profile", kwargs={"username": f"{self.user}"})
                + "?page=2"
            ): ONE_RECORD,
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertEqual(len(value.context["page_obj"]), expected)

    def test_form_context(self):
        response = self.authorized_client.get(reverse("posts:post_create"))
        get_form = response.context.get("form")
        self.assertIsInstance(get_form, PostForm)
        self.assertFalse(response.context["is_edit"])
