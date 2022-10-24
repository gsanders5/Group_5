from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import Account, Post, PostList



class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text="Required. Add a valid email address.")
    first_name = forms.CharField(max_length=255, help_text="Required. Add a first name.")
    last_name = forms.CharField(max_length=255, help_text="Required. Add a last name.")

    class Meta:
        model = Account
        fields = ('email', 'username', 'password1', 'password2', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError(f"Email {email} is already in use.")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError(f"Username {username} is already in use.")


class AccountAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ("email", "password")

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid Login")


class AccountUpdateForm(forms.ModelForm):
    bio = forms.CharField(label="Bio", required=False, widget=forms.Textarea)

    class Meta:
        model = Account
        fields = ('username', 'email', 'profile_image', 'first_name', 'last_name', 'bio', 'hide_email')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError(f"Email {email} is already in use.")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            account = Account.objects.exclude(pk=self.instance.pk).get(username=username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError(f"Username {username} is already in use.")

    def save(self, commit=True):
        account = super(AccountUpdateForm, self).save(commit=False)
        account.username = self.cleaned_data['username']
        account.email = self.cleaned_data['email'].lower()
        account.profile_image = self.cleaned_data['profile_image']
        account.hide_email = self.cleaned_data['hide_email']
        account.first_name = self.cleaned_data['first_name']
        account.last_name = self.cleaned_data['last_name']
        account.bio = self.cleaned_data['bio']
        if commit:
            account.save()
        return account


class PostCreationForm(forms.ModelForm):
    # def __init__(self, user, *args, **kwargs):
    #     self.user = kwargs.pop('user', None)
    #     super(PostCreationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ('text_content', 'is_image')




