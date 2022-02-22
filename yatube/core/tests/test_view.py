import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, User
from django import forms

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author_Leo')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug',
            description='Картинки',
        )

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        
    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.profile = reverse('posts:profile', args=[self.user.username])
        small_gif = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Сообщение 1',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

    def test_home_page_show_correct_context(self):
        index = self.authorized_client.get(reverse("posts:index"))
        profile = self.authorized_client.get(reverse('posts:profile', args=[self.user.username]))
        group = self.authorized_client.get(reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        detail = self.authorized_client.get(reverse('posts:post_detail', kwargs={'post_id': 1}))
        context_fields = {
            index.context['page_obj'][0].image: 'posts/small.gif',
            profile.context['page_obj'][0].image: 'posts/small.gif',
            group.context['page_obj'][0].image: 'posts/small.gif',
            detail.context['post'].image: 'posts/small.gif',
        }
        for value, expected in context_fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
