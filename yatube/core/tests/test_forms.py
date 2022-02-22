import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, User

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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.profile = reverse('posts:profile', args=[self.user.username])

    def test_create_task(self):
        tasks_count = Post.objects.count() 
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
        prof = reverse('posts:profile', args=[self.user.username])
        self.assertRedirects(response, prof)
        self.assertEqual(Post.objects.count(), tasks_count+1)
        self.assertTrue(
            Post.objects.filter(
                text='Сообщение 1',
                image='posts/small.gif'
            ).exists())
