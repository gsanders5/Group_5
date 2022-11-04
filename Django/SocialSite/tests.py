from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model


# Create your tests here.
class SignUpPageTests(TestCase):
    def setUp(self) -> None:
        self.username = 'testuser'
        self.email = 'testuser@email.com'
        self.first_name ='John'
        self.last_name = 'Smith'
        self.password = 'password'

    def test_signup_page_url(self):
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)
        #self.assertTemplateUsed(response, template_name='SocialSite/register.html,')

    def test_signup_page_view_name(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        #self.assertTemplateUsed(response, template_name='SocialSite/register.html,')

    def test_signup_form(self):
        response = self.client.post(reverse('register'), data={
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password1': self.password,
            'password2': self.password
        })
        
        self.assertEqual(response.status_code, 200)

        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 1)
