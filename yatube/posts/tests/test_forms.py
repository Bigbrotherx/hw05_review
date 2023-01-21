from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )

        cls.uploaded_2 = SimpleUploadedFile(
            name='small2.gif',
            content=small_gif,
            content_type='image/gif'
        )


        cls.user = User.objects.create_user(username='StasBasov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание',
        )

        # Создать один пост
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test post',
            group=cls.group,
        )

    @classmethod
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_post_in_db_autorized_user(self):
        post_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': self.uploaded
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        created_post = Post.objects.get(pk=Post.objects.first().pk)

        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.author, self.post.author)
        self.assertEqual(created_post.group, self.group)
        self.assertEqual(created_post.image, self.post.image)

    def test_edit_post_in_db(self):#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Edit post',
            'group': self.group.id,
            'image': self.uploaded_2
        }
        post_to_edit = Post.objects.get(text='Test post')
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_to_edit.id}),
            data=form_data,
            follow=True,
        )

        created_post = Post.objects.get(pk=Post.objects.first().pk)

        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': post_to_edit.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.author, self.post.author)
        self.assertEqual(created_post.group, self.group)
        self.assertEqual(created_post.image, form_data['image'])#!!!!!!!!!!!

    def test_add_post_in_db_not_autorized_user(self):
        post_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': self.uploaded

        }

        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_URL)
            + '?next=' + reverse('posts:post_create')
        )
        self.assertEqual(Post.objects.count(), post_count)
