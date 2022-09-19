from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Profile, FriendList, Post
from .serializers import ProfileSerializer


# implementation of sample API: https://www.youtube.com/watch?v=0UKWcv0og-Y&list=PLgCYzUzKIBE9KUJZJUmnDFYQfVyXYjX6r&index=1

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


@api_view()
def getUserProfile(request):
    # change to request's data -> id of current user
    profile = get_object_or_404(Profile, phoneNumber='901-570-5688')
    # profile = Profile.objects.get(phoneNumber='901-570-5688')
    serializer = ProfileSerializer(profile)
    return Response(serializer.data)


@api_view()
def getProfileById(request, profileId):
    try:
        # get id from request
        profile = get_object_or_404(Profile, phoneNumber='901-570-5688')

        profile = Profile.objects.get(id=profileId)
        serializer = ProfileSerializer(profile)

    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    return Response(serializer.data)
