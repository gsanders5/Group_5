from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Account, FriendList, Post
from .serializers import ProfileSerializer
from .forms import RegistrationForm


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
            destination = kwargs.get("next")
            if destination:
                return redirect(destination)
            return redirect("home")

        else:
            context['registration_form'] = form
    return render(request, 'SocialSite/register.html', context)


@api_view(['POST'])
def newUser(request):
    # create user with request.data validated
    # create friendList
    # create postList
    return Response()


@api_view(['GET'])
def getFriends(request):
    # get friendList
    # Serialize?
    return Response()


@api_view(['GET'])
def getPosts(request):
    # get postList
    # Serialize?
    return Response()


# @api_view()
# def getUserProfile(request):
#     # change to request's data -> id of current user
#     # profile = get_object_or_404(Profile, phoneNumber='901-570-5688')
#     # profile = Profile.objects.get(phoneNumber='901-570-5688')
#     serializer = ProfileSerializer(profile)
#     return Response(serializer.data)


# @api_view()
# def getProfileById(request, profileId):
#     try:
#         # get id from request
#         # profile = get_object_or_404(Profile, phoneNumber='901-570-5688')
#
#         # profile = Profile.objects.get(id=profileId)
#         # serializer = ProfileSerializer(profile)
#
#     except Profile.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     return Response(serializer.data)
