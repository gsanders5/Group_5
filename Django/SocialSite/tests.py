from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from SocialSite.models import Account, Post


# Create your tests here.
class SignUpPageTestsValid(TestCase):
    def setUp(self) -> None:
        self.username = 'testuser'
        self.email = 'testuser@email.com'
        self.first_name = "test"
        self.last_name = "case"
        self.password = 'ASHJKhadfGH123456!'


    def test_signup_form(self):
        response = self.client.post(reverse('register'), data={
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password1': self.password,
            'password2': self.password,
        })
        # 302 means redirect which means account was created successfully
        self.assertEqual(response.status_code, 302)

        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 1)


class SignUpPageTestsInsecurePassword(TestCase):
    def setUp(self) -> None:
        self.username = 'testuser'
        self.email = 'testuser@email.com'
        self.first_name = "test"
        self.last_name = "case"
        self.password = 'password!'

    def test_signup_page_view_name(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        assert 'SocialSite/register.html' in (t.name for t in response.templates)

    def test_signup_form(self):
        response = self.client.post(reverse('register'), data={
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password1': self.password,
            'password2': self.password,
        })
        # 200 is if password or any field is bad.
        self.assertEqual(response.status_code, 200)

        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 0)


class SignUpPageTestsDuplicateEmail(TestCase):
    def setUp(self) -> None:
        newAccount = Account(email="testuser@email.com", first_name="test", last_name="user", username="testuser", password="ERTYfcdRErt432!")
        newAccount.save()
        self.username = 'testuser'
        self.email = 'testuser@email.com'
        self.first_name = "test"
        self.last_name = "case"
        self.password = 'password!'

    def test_signup_page_url(self):
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)

    def test_signup_form(self):
        response = self.client.post(reverse('register'), data={
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password1': self.password,
            'password2': self.password,
        })
        # 200 is if password or any field is bad.
        self.assertEqual(response.status_code, 200)

        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 1)


class LoginPageTests(TestCase):
    def setUp(self) -> None:
        self.email = 'testuser@email.com'
        self.password = 'ERTYfcdRErt432!'

    def test_login_page_url(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)

    def test_login_page_view_name(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        assert 'SocialSite/login.html' in (t.name for t in response.templates)

    def test_login_form_bad_login(self):
        response = self.client.post(reverse('login'), data={
            'email': self.email,
            'password': self.password,
        })
        # 200 means redirect which means account was created successfully
        self.assertEqual(response.status_code, 200)

        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 0)



class PostCreationTests(TestCase):
    def setUp(self) -> None:
        self.username = 'testuser'
        self.email = 'testuser@email.com'
        self.first_name = "test"
        self.last_name = "case"
        self.password = 'ASHJKhadfGH123456!'
        self.client.post(reverse('register'), data={
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password1': self.password,
            'password2': self.password,
        })
        self.text_content = 'testingtestingtesting'
        self.is_image = False

        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 1)

    def test_post_create_url(self):
        response = self.client.get("/create/")
        self.assertEqual(response.status_code, 200)

    def test_post_create_view_name(self):
        response = self.client.get(reverse('create-post'))
        self.assertEqual(response.status_code, 200)
        assert 'SocialSite/Post/create_post.html' in (t.name for t in response.templates)
        assert 'SocialSite/Post/create_post_js.html' in (t.name for t in response.templates)

    def test_post_creation_form(self):
        response = self.client.post(reverse('create-post'), data={
            'text_content': self.text_content,
            'is_image': self.is_image,
        })
        # 302 means redirect which means account was created successfully
        self.assertEqual(response.status_code, 302)

        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 1)
        posts = Post.objects.all()
        self.assertEqual(posts.count(), 1)
