from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Account, FriendList, Post
from .serializers import ProfileSerializer
from .forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm


# implementation of sample API: https://www.youtube.com/watch?v=0UKWcv0og-Y&list=PLgCYzUzKIBE9KUJZJUmnDFYQfVyXYjX6r&index=1

def register_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return HttpResponse(f"You are already authenticated as {user.email}.")
    context = {}

    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            destination = get_redirect_if_exists(request)
            if destination:
                return redirect(destination)
            return redirect("home")

        else:
            context['registration_form'] = form
    return render(request, 'SocialSite/register.html', context)


def logout_view(request):
    logout(request)
    return redirect("home")


def login_view(request, *args, **kwargs):
    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect("home")

    destination = get_redirect_if_exists(request)
    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                destination = get_redirect_if_exists(request)
                if destination:
                    return redirect(destination)
                return redirect("home")
        else:
            context['login_form'] = form
    return render(request, "SocialSite/login.html", context)


def get_redirect_if_exists(request):
    userRedirect = None
    if request.GET:
        if request.GET.get("next"):
            userRedirect = str(request.GET.get("next"))
    return userRedirect


def account_view(request, *args, **kwargs):
    context = {}
    user_id = kwargs.get("user_id")

    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse("That user doesn't exist.")
    if account:
        context['id'] = account.id
        context['username'] = account.username
        context['email'] = account.email
        context['profile_image'] = account.profile_image.url
        context['hide_email'] = account.hide_email
        context['first_name'] = account.first_name
        context['last_name'] = account.last_name
        context['bio'] = account.bio
        context['is_private'] = account.isPrivate

        is_self = True
        is_friend = False
        user = request.user
        if user.is_authenticated and user != account:
            is_self = False
        elif not user.is_authenticated:
            is_self = False

        context['is_self'] = is_self
        context['is_friend'] = is_friend
        context['BASE_URL'] = settings.BASE_URL

        return render(request, 'SocialSite/Account/account.html', context)


def account_search_view(request, *args, **kwargs):
    context = {}

    if request.method == "GET":
        search_query = request.GET.get("q")
        if len(search_query) > 0:
            search_results = Account.objects.filter(email__icontains=search_query).filter(
                username__icontains=search_query).distinct()
            user = request.user
            accounts = []
            for account in search_results:
                accounts.append((account, False))
            context['accounts'] = accounts

    return render(request, "SocialSite/Account/search_results.html", context)


def edit_account_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    user_id = kwargs.get("user_id")
    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse("Something went wrong.")
    if account.pk != request.user.pk:
        return HttpResponse("You cannot someone else's profile.")
    context = {}
    if request.POST:
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("view", user_id=account.pk)
        else:
            form = AccountUpdateForm(request.POST, instance=request.user,
                                     initial={
                                         "id": account.pk,
                                         "email": account.email,
                                         "username": account.username,
                                         "first_name": account.first_name,
                                         "last_name": account.last_name,
                                         "hide_email": account.hide_email,
                                         "profile_image": account.profile_image,
                                         "bio": account.bio,

                                     }
                                     )
            context['form'] = form
    else:
        form = AccountUpdateForm(
                                 initial={
                                     "id": account.pk,
                                     "email": account.email,
                                     "username": account.username,
                                     "first_name": account.first_name,
                                     "last_name": account.last_name,
                                     "hide_email": account.hide_email,
                                     "profile_image": account.profile_image,
                                     "bio": account.bio,

                                 }
                                 )
        context['form'] = form
    context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    return render(request, "SocialSite/Account/edit_account.html", context)

