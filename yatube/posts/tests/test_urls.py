from http import HTTPStatus

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase


from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        cache.clear()
        self.guest_client = Client()

        # Создаем авторизованный клиент
        # 1. Создаем пользователя
        self.user = User.objects.create_user(username='noname')
        # 2. Создаем второй клиент
        self.authorized_client = Client()
        # 3. Авторизуем пользователя
        self.authorized_client.force_login(self.user)

        # Создаем автора поста и логиним его
        self.author_client = Client()
        self.author_client.force_login(PostsURLTests.user)

        self.index = '/'
        self.group_list = f'/group/{self.group.slug}/'
        self.profile = f'/profile/{self.user.get_username()}/'
        self.post_detail = f'/posts/{self.post.pk}/'
        self.post_edit = f'/posts/{self.post.pk}/edit/'
        self.post_create = '/create/'
        self.unexisting = '/unexisting_page/'

        self.index_html = 'posts/index.html'
        self.group_list_html = 'posts/group_list.html'
        self.profile_html = 'posts/profile.html'
        self.post_detail_html = 'posts/post_detail.html'
        self.post_edit_html = 'posts/create_post.html'
        self.post_create_html = 'posts/create_post.html'
        self.not_found = 'core/404.html'

        self.url_client_template_dict = {
            self.index: (self.guest_client, self.index_html),
            self.group_list: (self.guest_client, self.group_list_html),
            self.profile: (self.guest_client, self.profile_html),
            self.post_detail: (self.guest_client, self.post_detail_html),
            self.post_edit: (self.author_client, self.post_edit_html),
            self.post_create: (self.authorized_client, self.post_create_html),
            self.unexisting: (self.guest_client, None),
        }

    def test_url_exists_at_desired_location(self):
        """
        Страница доступна по ожидаемому адресу для ожидаемого типа
        пользователя.
        """
        for url, (client, useless) in self.url_client_template_dict.items():
            with self.subTest(url=url):
                response = client.get(url)
                if url == '/unexisting_page/':
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.NOT_FOUND)

    def test_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, (client, template) in self.url_client_template_dict.items():
            with self.subTest(url=url):
                if url == '/unexisting_page/':
                    continue
                response = client.get(url)
                self.assertTemplateUsed(response, template)

    def test_pages_for_all(self):
        """Страницы доступны всем пользователям"""
        urls = {
            self.index: HTTPStatus.OK,
            self.group_list: HTTPStatus.OK,
            self.profile: HTTPStatus.OK,
            self.post_detail: HTTPStatus.OK,
            self.unexisting: HTTPStatus.NOT_FOUND,
            self.post_create: HTTPStatus.FOUND,
            self.post_edit: HTTPStatus.FOUND
        }
        for address, code in urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_pages_for_authorized_client(self):
        """Страницы доступны авторизованному пользователю"""
        urls = {
            self.index: HTTPStatus.OK,
            self.group_list: HTTPStatus.OK,
            self.profile: HTTPStatus.OK,
            self.post_detail: HTTPStatus.OK,
            self.unexisting: HTTPStatus.NOT_FOUND,
            self.post_create: HTTPStatus.OK,
            self.post_edit: HTTPStatus.FOUND
        }
        for address, code in urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_pages_for_author(self):
        """Страницы доступны автору"""
        urls = {
            self.index: HTTPStatus.OK,
            self.group_list: HTTPStatus.OK,
            self.profile: HTTPStatus.OK,
            self.post_detail: HTTPStatus.OK,
            self.unexisting: HTTPStatus.NOT_FOUND,
            self.post_create: HTTPStatus.OK,
            self.post_edit: HTTPStatus.OK
        }
        for address, code in urls.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_error_not_found_page(self):
        response = self.client.get(self.unexisting)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, self.not_found )