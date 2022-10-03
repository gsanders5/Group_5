from rest_framework import serializers
from .models import FriendList, Account, Post


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        # not safe to display in browser -> email/phoneNumber
        model = Account
        fields = ['email', 'username', 'first_name', 'last_name']
    # id = serializers.IntegerField()
    # firstName = serializers.CharField(max_length=255)
    # lastName = serializers.CharField(max_length=255)
    # email = serializers.CharField(max_length=254)
    # phoneNumber = serializers.CharField(max_length=255)
    # bio = serializers.CharField()


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['userid', 'numOfLikes', 'content', 'createdAt', 'usersWhoLiked']
