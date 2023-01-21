from math import ceil

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()


class PostVievTest(TestCase):#!!!!!!!!!!!!!!!!!!!!!!!
    @classmethod
    def setUpClass(cls):
        cache.clear()
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
            content_type='image/gif'
        )

        cls.user = User.objects.create_user(username='StasBasov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание',
        )
    def setUp(self):
        cache.clear()
        self.post = Post.objects.create(
            author=self.user,
            text='Test post',
            group=self.group,
            image=self.uploaded
        )

        self.index_html = 'posts/index.html'
        self.group_list_html = 'posts/group_list.html'
        self.profile_html = 'posts/profile.html'
        self.post_detail_html = 'posts/post_detail.html'
        self.post_edit_html = 'posts/create_post.html'
        self.post_create_html = 'posts/create_post.html'

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): self.index_html,
            (reverse('posts:group_list', kwargs={'slug':
                     self.group.slug})): self.group_list_html,
            (reverse('posts:profile', kwargs={'username':
                     self.user.username})): self.profile_html,
            (reverse('posts:post_detail', kwargs={'post_id':
                     self.post.id})): self.post_detail_html,
            (reverse('posts:post_edit', kwargs={'post_id':
                     self.post.id})): self.post_edit_html,
            reverse('posts:post_create'): self.post_create_html
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(template)
            self.assertTemplateUsed(response, reverse_name)

    # Проверка словаря контекста главной страницы
    def test_home_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        object_data = {
            first_object.text: self.post.text,
            first_object.author: self.user,
            first_object.group: self.post.group,
            first_object.pub_date: self.post.pub_date,
            first_object.image: self.post.image
        }
        for obj, data in object_data.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, data)

    def test_group_list_shows_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        object_data = {
            first_object.text: self.post.text,
            first_object.author: self.user,
            first_object.group: self.post.group,
            first_object.pub_date: self.post.pub_date,
            first_object.image: self.post.image,
            response.context['group']: self.group,
        }
        for obj, data in object_data.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, data)

    def test_profile_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username})
        )
        first_object = response.context['page_obj'][0]
        author_posts = Post.objects.select_related(
            'author').filter(author__username=self.user.username)
        object_data = {
            first_object.author: self.user,
            first_object.image: self.post.image,
            response.context['author']: self.user,
        }
        for obj, data in object_data.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, data)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        response_context = response.context['post']
        post_text = {
            response_context.text: 'Тестовый пост',
            response_context.group: self.group,
            response_context.author: self.user.username,
            response_context.image: self.post.image
        }
        for value, expected in post_text.items():
            self.assertEqual(post_text[value], expected)

    def test_post_editing_shows_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['is_edit'], True)

    def test_post_creation_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_in_index(self):
        response = self.authorized_client.get(reverse(
            'posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object, self.post)

    def test_post_in_correct_group(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group, self.group)

    def test_post_in_correct_user(self):
        response = self.client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object, self.post)

    def test_cash_index_page(self):
        response_0 = self.authorized_client.get('/', follow=True)
        Post.objects.all().delete()
        response_1 = self.authorized_client.get('/', follow=True)
        self.assertEqual(response_0.content, response_1.content)
        cache.clear()
        response_2 = self.authorized_client.get('/', follow=True)
        self.assertNotEqual(response_0.content, response_2.content)

class PostPaginationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cache.clear()
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.some_group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание',
        )

        cls.post_list = []
        for i in range(0, 22):
            cls.post_list.append(Post(text=f'Test post -{i}',
                                      group=cls.some_group,
                                      author=cls.user))
        Post.objects.bulk_create(cls.post_list)
        cls.post_count = Post.objects.count()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_records(self):
        test_set = {
            reverse('posts:index'),
            reverse('posts:profile',
                    kwargs={'username': self.user.username}),
            reverse('posts:group_list',
                    kwargs={'slug': self.some_group.slug})
        }
        for reverse_response in test_set:
            with self.subTest(reverse_response=reverse_response):
                response = self.authorized_client.get(reverse_response)
                self.assertEqual(
                    len(response.context['page_obj']), settings.POSTS_QUANTITY
                )

    def test_last_page_contains_records(self):
        last_page_number = ceil((self.post_count / settings.POSTS_QUANTITY))
        numb_of_posts_on_the_last_page = self.post_count % settings.POSTS_QUANTITY
        test_set = {
            f'''{reverse('posts:index')}?page={last_page_number}''',
            f'''{reverse('posts:profile',
            kwargs={'username': self.user.username})}?page={last_page_number}''',
            f'''{reverse('posts:group_list',
            kwargs={'slug': self.some_group.slug})}?page={last_page_number}'''
        }
        for reverse_response in test_set:
            with self.subTest(reverse_response=reverse_response):
                response = self.authorized_client.get(reverse_response)
                self.assertEqual(
                    len(response.context['page_obj']),
                    numb_of_posts_on_the_last_page
                )


class PostCommentsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cache.clear()
        super().setUpClass()
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

    def test_add_comment_in_db_not_autorized_user (self):
        comments_count = Comment.objects.count()
        form_data ={
            'text': 'Test comment'
        }
        self.guest_client.post(
            reverse('posts:add_comment', args='1'),
            data=form_data,
            follow=True
        )

        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertFalse(Comment.objects.filter(
            text = form_data['text']).exists())

    def test_add_comment_in_db_autorized_user (self):
        comments_count = Comment.objects.count()
        form_data ={
            'text': 'Test comment'
        }
        self.authorized_client.post(
            reverse('posts:add_comment', args='1'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count+1)
        self.assertTrue(Comment.objects.filter(
            text = form_data['text']).exists())
