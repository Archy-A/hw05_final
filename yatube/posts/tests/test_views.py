from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()
POSTS_NUMBER = 30


class PostVIEWTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.not_author = User.objects.create_user(username='not_author')

        for i in range(POSTS_NUMBER):
            cls.slug = f'test_group_{i}'
            cls.group = Group.objects.create(
                title='Тестовая группа',
                slug=f'test_group_{i}',
                description='Тестовое описание'
            )
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовая запись',
                group=cls.group,
            )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = PostVIEWTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_author = PostVIEWTests.not_author
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.not_author)

    def test_uses_correct_template(self):
        views_template = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', 
                    kwargs={'slug': f'{PostVIEWTests.post.group.slug}'}):
                    'posts/group_list.html',
            reverse('posts:profile', kwargs={'username':
                    f'{PostVIEWTests.user}'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id':
                    f'{PostVIEWTests.post.id}'}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id':
                    f'{PostVIEWTests.post.id}'}): 'posts/create_post.html'
        }
        for address, template in views_template.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_context_post_detail(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id':
                    f'{PostVIEWTests.post.id}'}))
        post = response.context.get('post')
        context_fields = {
            post.text: 'Тестовая запись',
            post.author.username: 'auth',
            post.group.title: 'Тестовая группа',
            post.group.description: 'Тестовое описание',
            post.group.slug: f'test_group_{POSTS_NUMBER-1}'
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_context_index(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)
        self.assertTrue(len(response.context.get('page_obj').object_list) > 0)
        post = response.context['page_obj'][0]
        context_fields = {
            'id': post.id,
            'text': post.text,
            'pub_date': post.pub_date,
            'author': post.author,
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertIsNotNone(expected)

        cont = response.context
        context_fields = {
            cont['page_obj'][0].text: 'Тестовая запись',
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_context_grouplist(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_group_1'}))
        self.assertEqual(len(response.context.get('page_obj').object_list), 1)
        groupcontext = response.context['page_obj'][0]
        context_fields = {
            'id': groupcontext.id,
            'text': groupcontext.text,
            'pub_date': groupcontext.pub_date,
            'author': groupcontext.author,
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertIsNotNone(expected)

        cont = response.context
        context_fields = {
            cont['group'].title: 'Тестовая группа',
            cont['page_obj'][0].text: 'Тестовая запись',
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_context_profile(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'}))
        profilecontext = response.context['page_obj'][0]
        context_fields = {
            'id': profilecontext.id,
            'text': profilecontext.text,
            'pub_date': profilecontext.pub_date,
            'author': profilecontext.author,
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertIsNotNone(expected)

        cont = response.context
        context_fields = {
            cont['user'].username: 'auth',
            cont['page_obj'][0].text: 'Тестовая запись',
            cont['post_count']: 30
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_context_post_create(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.models.ModelChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Текст формы'
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        post = Post.objects.all().first()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.user)
        self.assertRedirects(
            response, reverse('posts:profile', args=(self.user.username,))
        )

    def test_context_post_edit(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id':
                    f'{PostVIEWTests.post.id}'}))
        form_fields = {
            'group': forms.models.ModelChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
