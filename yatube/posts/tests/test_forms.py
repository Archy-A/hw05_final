from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User
from http import HTTPStatus


POSTS_NUMBER = 30

class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author_Leo')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug',
            description='testing',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug2',
            description='Описание',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.profile = reverse('posts:profile', args=[self.user.username])

    def test_create_post(self):
        form_data = {
            'text': 'Сообщение 1',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        prof = reverse('posts:profile', kwargs={'username': 'Author_Leo'})
        post = Post.objects.all().filter(id=1)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post[0].text, form_data['text'])
        self.assertEqual(post[0].group, self.group)
        self.assertEqual(post[0].author, self.user)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, prof)
        response = self.authorized_client.get(reverse('posts:post_create'))
        get_form = response.context.get('form')
        self.assertIsInstance(get_form, PostForm)
        self.assertFalse(response.context['is_edit'])

    def test_post_edit(self):
        self.post = Post.objects.create(
            author=self.user,
            text='Сообщение 3',
            group=self.group,
        )
        form_data = {
            'text': 'Сообщение 4',
            'group': self.group2.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )

        self.post.refresh_from_db()
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(self.post.text, form_data['text'])
        self.assertEqual(self.post.group, self.group2)
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        prof = reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        self.assertRedirects(response, prof)
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                     kwargs={'post_id': f'{self.post.id}'}))
        get_form = response.context.get('form')
        self.assertIsInstance(get_form, PostForm)
        self.assertTrue(response.context['is_edit'])