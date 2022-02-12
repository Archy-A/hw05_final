from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Test',
            slug='test_slug',
            description='testing',
        )
        cls.group2 = Group.objects.create(
            title='Test2',
            slug='test_slug2',
            description='Описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test_post',
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.profile = reverse('posts:profile', args=[self.user.username])

    def test_new_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for name, expected in form_fields.items():
            with self.subTest(name=name):
                field_filled = response.context.get('form').fields.get(name)
                self.assertIsInstance(field_filled, expected)

    def test_edit_page_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id':
                    f'{PostFormTests.post.id}'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for name, expected in form_fields.items():
            with self.subTest(name=name):
                field_filled = response.context.get('form').fields.get(name)
                self.assertIsInstance(field_filled, expected)

    def test_create_post(self):
        post = Post.objects.count()
        form_data = {
            'text': 'Тестовое сообщение',
            'group': self.group.id,

        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        prof = reverse('posts:profile', kwargs={'username': 'user'})
        post = response.context['page_obj'][0]
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, prof)

    def test_post_edit(self):
        post = Post.objects.first()
        form_data = {
            'text': 'Новое сообщение',
            'group': self.group2.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                    'post_id': f'{PostFormTests.post.id}'}),
            data=form_data,
            follow=True
        )
        post = response.context['post']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group2)
        self.assertEqual(post.author, self.user)
        self.assertEqual(response.status_code, 200)

    def test_post_in_url(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(PostFormTests.post, response.context['page_obj'][0])

    def test_post_not_in_group2(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug2'}))
        self.assertNotIn(PostFormTests.post, response.context.get('page_obj'))
