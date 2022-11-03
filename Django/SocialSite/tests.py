from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model


# Create your tests here.
class SignUpPageTests(TestCase):
    def setUp(self) -> None:
        self.username = 'testuser'
        self.email = 'testuser@email.com'
        self.age = 20
        self.password = 'password'

    def test_signup_page_url(self):
        response = self.client.get("/users/signup/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='signup.html')

    def test_signup_page_view_name(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='signup.html')

    def test_signup_form(self):
        response = self.client.post(reverse('signup'), data={
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'password1': self.password,
            'password2': self.password
        })
        self.assertEqual(response.status_code, 200)

        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 1)
