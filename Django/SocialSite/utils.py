from .models import FriendRequest, Account, PostList, Post
from django.http import HttpResponse


def get_friend_request_or_false(sender, receiver):
    try:
        return FriendRequest.objects.get(sender=sender, receiver=receiver, is_active=True)
    except FriendRequest.DoesNotExist:
        return False


def create_post_list_jobs(request):
    accounts = Account.objects.all()
    for account in accounts:
        try:
            PostList.objects.get(user=account)
        except PostList.DoesNotExist:
            new_post_list = PostList(user=account)
            new_post_list.save()
    return True



def add_user_to_posts(request):
    allPosts = Post.objects.all()
    allPostLists = PostList.objects.all()
    for post in allPosts:
        for postList in allPostLists:
            try:
                userPost = postList.posts.get(id=post.id)
                if userPost:
                    userPost.poster = postList.user
                    userPost.save()
                    break
                else:
                    continue
            except Post.DoesNotExist:
                continue;

