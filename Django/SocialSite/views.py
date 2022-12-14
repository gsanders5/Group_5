from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core import files
from .models import Account, FriendList, FriendRequest, PostList, Post, CommentList, Comment
from .friend_request_status import FriendRequestStatus
from .forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm, PostCreationForm, CommentCreationForm, PostUpdateForm
from .utils import get_friend_request_or_false, create_post_list_jobs, add_user_to_posts
import os
import cv2
import base64
import requests
import json
import random
import io
import string
import types

TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"
TEMP_POST_IMAGE_NAME = "tempPostImage.png"

# Outputs Register Page with Form (errors/no errors)
# Logs in user after registration
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


# Logs out user redirects to Homepage
def logout_view(request):
    logout(request)
    return redirect("home")


# Login View with form validation and authentication
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


# Gets redirect
def get_redirect_if_exists(request):
    userRedirect = None
    if request.GET:
        if request.GET.get("next"):
            userRedirect = str(request.GET.get("next"))
    return userRedirect


#Home page view with friends posts
def home_view(request, *args, **kwargs):
    context = {}
    user = request.user
    if user.is_authenticated:
        context['id'] = user.id
        context['username'] = user.username
        context['profile_image'] = user.profile_image.url
        # Gets friends list
        try:
            friend_list = FriendList.objects.get(user=user)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=user)
            friend_list.save()

        friends = friend_list.friends.all()
        context['friends'] = friends
        all_posts = []
        # Get all posts from friends and user post lists
        try:
            user_post_list = PostList.objects.get(user=user)
        except PostList.DoesNotExist:
            user_post_list = PostList(user=user)
            user_post_list.save()
        if user_post_list:
            user_posts = user_post_list.posts.all()
            for post in user_posts:
                user_post_object = types.SimpleNamespace()
                user_post_object.friend = user
                user_post_object.post = post
                has_liked = False
                try:
                    has_liked = post.usersWhoLiked.get(id=user.id)
                    if has_liked:
                        user_post_object.has_liked = True
                except:
                    user_post_object.has_liked = False
                all_posts.append(user_post_object)
        for friend in friends:
            try:
                friend_post_list = PostList.objects.get(user=friend)
            except PostList.DoesNotExist:
                friend_post_list = PostList(user=friend)
                friend_post_list.save()
            if friend_post_list:
                friend_posts = friend_post_list.posts.all()
                for post in friend_posts:
                    friend_post_object = types.SimpleNamespace()
                    friend_post_object.friend = friend
                    friend_post_object.post = post
                    has_liked = False
                    try:
                        has_liked = post.usersWhoLiked.get(id=user.id)
                        if has_liked:
                            friend_post_object.has_liked = True
                    except:
                        friend_post_object.has_liked = False
                    all_posts.append(friend_post_object)
        all_posts.sort(key=lambda x: x.post.created_at, reverse=True)
        context['posts'] = all_posts
        return render(request, 'SocialSite/home.html', context)
    return redirect('login')



# Account page view
# Manages friend requests
def account_view(request, *args, **kwargs):
    context = {}
    user_id = kwargs.get("user_id")
    # Get page's Account from DB based on user_id
    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse("That user doesn't exist.")

    if account:
        # Set necessary fields
        context['id'] = account.id
        context['username'] = account.username
        context['email'] = account.email
        context['profile_image'] = account.profile_image.url
        context['hide_email'] = account.hide_email
        context['first_name'] = account.first_name
        context['last_name'] = account.last_name
        context['bio'] = account.bio
        context['is_private'] = account.isPrivate
        all_posts = []
        # Get accounts friend list
        # If it doesn't exist, make one
        try:
            friend_list = FriendList.objects.get(user=account)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=account)
            friend_list.save()
        friends = friend_list.friends.all()
        context['friends'] = friends

        # Set initial variables
        is_self = True
        is_friend = False
        request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
        friend_requests = None
        user = request.user
        # If user is logged in and is not viewing own profile
        if user.is_authenticated and user != account:
            is_self = False
            # If user is friend of the account being viewed
            if friends.filter(pk=user.id):
                is_friend = True
                # Get accounts post list if friend
                # If it doesn't exist, make one
                try:
                    post_list = PostList.objects.get(user=account)
                except PostList.DoesNotExist:
                    post_list = PostList(user=Account)
                    post_list.save()
                posts = post_list.posts.all()
                post_list = list(posts)
                post_list.sort(key=lambda x: x.created_at, reverse=True)
                num_of_posts = posts.count()
                context['posts'] = post_list
                context['num_of_posts'] = num_of_posts
            # If user is not friends with account
            # Check for friend request
            else:
                is_friend = False
                if get_friend_request_or_false(sender=account, receiver=user):
                    request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                    context['pending_friend_request_id'] = get_friend_request_or_false(sender=account, receiver=user).id
                elif get_friend_request_or_false(sender=user, receiver=account):
                    request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
                else:
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
        # If user is not logged in
        elif not user.is_authenticated:
            is_self = False

        # If user is viewing own profile
        else:
            # Get user's pending friend requests
            try:
                friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
            except:
                pass
            try:
                post_list = PostList.objects.get(user=account)
            except PostList.DoesNotExist:
                post_list = PostList(user=Account)
                post_list.save()
            if post_list:
                user_posts = post_list.posts.all()
                for post in user_posts:
                    user_post_object = types.SimpleNamespace()
                    user_post_object = post
                    has_liked = False
                    try:
                        has_liked = post.usersWhoLiked.get(id=user.id)
                        if has_liked:
                            user_post_object.has_liked = True
                    except:
                        user_post_object.has_liked = False
                    all_posts.append(user_post_object)
                all_posts.sort(key=lambda x: x.created_at, reverse=True)
            num_of_posts = len(all_posts)
            context['posts'] = all_posts
            context['num_of_posts'] = num_of_posts

        # Give context necessary variables
        context['is_self'] = is_self
        context['is_friend'] = is_friend
        context['BASE_URL'] = settings.BASE_URL
        context['request_sent'] = request_sent
        context['friend_requests'] = friend_requests
        return render(request, 'SocialSite/Account/account.html', context)


# Account search view
def account_search_view(request, *args, **kwargs):
    context = {}

    if request.method == "GET":
        search_query = request.GET.get("q")
        filter_options = request.GET.get("f")
        if len(search_query) > 0:
            context['query'] = search_query
            search_results = Account.objects.filter(username__icontains=search_query).distinct()
            user = request.user
            accounts = []
            if user.is_authenticated:
                auth_user_friend_list = FriendList.objects.get(user=user)
                for account in search_results:
                    if filter_options == "True":
                        if account == user:
                            continue
                        if auth_user_friend_list.is_mutual_friend(account):
                            accounts.append((account, auth_user_friend_list.is_mutual_friend(account)))
                    elif filter_options == "False":
                        if account == user:
                            continue
                        if not auth_user_friend_list.is_mutual_friend(account):
                            accounts.append((account, auth_user_friend_list.is_mutual_friend(account)))
                    else:
                        accounts.append((account, auth_user_friend_list.is_mutual_friend(account)))

                context['accounts'] = accounts
            else:
                for account in search_results:
                    accounts.append((account, False))
                context['accounts'] = accounts

    return render(request, "SocialSite/Account/search_results.html", context)


# Edit account page with form
def edit_account_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    user_id = kwargs.get("user_id")
    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse("Something went wrong.")
    if account.pk != request.user.pk:
        return HttpResponse("You cannot edit someone else's profile.")
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


# Sends friend request
def send_friend_request(request, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            receiver = Account.objects.get(pk=user_id)
            try:
                friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver)
                try:
                    for request in friend_requests:
                        if request.is_active:
                            raise Exception("You already sent them a friend request.")
                    friend_request = FriendRequest(sender=user, receiver=receiver)
                    friend_request.save()
                    payload['response'] = "Friend request sent."
                except Exception as e:
                    payload['response'] = str(e)
            except FriendRequest.DoesNotExist:
                friend_request = FriendRequest(sender=user, receiver=receiver)
                friend_request.save()
                payload['response'] = "Friend Request sent."

            if payload['response'] is None:
                payload['response'] = "Something went wrong."
        else:
            payload['response'] = "Unable to send a friend request."
    else:
        payload['response'] = "You must be authenticated to send a friend request."
    return HttpResponse(json.dumps(payload), content_type="application/json")


# Shows all active friend requests
def friend_requests_view(request, *args, **kwargs):
    context = {}
    user = request.user
    if user.is_authenticated:
        user_id = kwargs.get("user_id")
        account = Account.objects.get(pk=user_id)
        if account == user:
            friend_requests = FriendRequest.objects.filter(receiver=account, is_active=True)
            context['friend_requests'] = friend_requests
        else:
            return HttpResponse("You can't view another user's friend requests.")
    else:
        redirect("login")
    return render(request, "SocialSite/Friend/friend_requests.html", context)


# Accepts active friend request
def accept_friend_request(request, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "GET" and user.is_authenticated:
        friend_request_id = kwargs.get("friend_request_id")
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            if friend_request.receiver == user:
                if friend_request:
                    friend_request.accept()
                    payload['response'] = "Friend request accepted."
                else:
                    payload['response'] = "Something went wrong."
            else:
                payload['response'] = "That is not your request to accept."
        else:
            payload['response'] = "Unable to accept that friend request."
    else:
        payload['response'] = "You must be authenticated to accept a friend request."
    return HttpResponse(json.dumps(payload), content_type="application/json")


# Remove friend
def remove_friend(request, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            try:
                removee = Account.objects.get(pk=user_id)
                friend_list = FriendList.objects.get(user=user)
                friend_list.unfriend(removee)
                payload['response'] = "Successfully removed that friend."
            except Exception as e:
                payload['response'] = f"Something went wrong: {str(e)}."
        else:
            payload['response'] = "There was an error. Unable to remove that friend."
    else:
        payload['response'] = "You must be authenticated to remove a friend."
    return HttpResponse(json.dumps(payload), content_type="application/json")


# Declines active friend request
def decline_friend_request(request, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "POST" and user.is_authenticated:
        friend_request_id = request.POST.get("friend_request_id")
        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            if friend_request.receiver == user:
                if friend_request:
                    friend_request.decline()
                    payload['response'] = "Friend request declined."
                else:
                    payload['response'] = "Something went wrong."
            else:
                payload['response'] = "That is not your friend request to decline."
        else:
            payload['response'] = "Unable to decline that friend request. "
    else:
        payload['response'] = "You must be authenticated to decline a friend request."
    return HttpResponse(json.dumps(payload), content_type="application/json")


# Cancel sent friend request
def cancel_friend_request(request, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            receiver = Account.objects.get(pk=user_id)
            try:
                friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver, is_active=True)
            except Exception as e:
                payload['response'] = "Nothing to cancel. Friend request does not exist."
            if len(friend_requests) > 1:
                for request in friend_requests:
                    request.cancel()
                payload['response'] = "Friend request cancelled."
            else:
                friend_requests.first().cancel()
                payload['response'] = "Friend request cancelled."
        else:
            payload['response'] = "Unable to cancel that friend request."
    else:
        payload['response'] = "You must be authenticated to cancel a friend request."
    return HttpResponse(json.dumps(payload), content_type="application/json")


# Displays account's Friend List
def friend_list_view(request, *args, **kwargs):
    user = request.user
    context = {}
    if user.is_authenticated:
        user_id = kwargs.get("user_id")
        if user_id:
            try:
                this_user = Account.objects.get(pk=user_id)
                context['this_user'] = this_user
            except Account.DoesNotExist:
                return HttpResponse("That user does not exist.")
            try:
                friend_list = FriendList.objects.get(user=this_user)
            except FriendList.DoesNotExist:
                return HttpResponse(f"Could not find a friends list for {this_user.username}")
            if user != this_user:
                if not user in friend_list.friends.all():
                    return HttpResponse("You must be friends to view their friends list.")
            friends = []
            auth_user_friend_list = FriendList.objects.get(user=user)
            for friend in friend_list.friends.all():
                friends.append((friend, auth_user_friend_list.is_mutual_friend(friend)))
            context['friends'] = friends
    else:
        return HttpResponse("You must be friends to view their friends list.")
    return render(request, "SocialSite/Friend/friend_list.html", context)


# View for Account's Post Page --> Not sure if implementing
def account_posts_view(request, *args, **kwargs):
    user = request.user
    context = {}
    if user.is_authenticated:
        user_id = kwargs.get("user_id")
        if user_id:
            try:
                this_user = Account.objects.get(pk=user_id)
                context['this_user'] = this_user
            except Account.DoesNotExist:
                return HttpResponse("That user does not exist.")
            try:
                friend_list = FriendList.objects.get(user=this_user)
                context['friend_list'] = friend_list
            except FriendList.DoesNotExist:
                return HttpResponse("That user does not have friends list.")
            try:
                post_list = PostList.objects.get(user=user_id)
                context['post_list'] = post_list
            except PostList.DoesNotExist:
                return HttpResponse("That user does not have a post list.")
            posts = []
            for post in post_list.posts.all():
                posts.append(post)
            context['posts'] = posts
        else:
            return HttpResponse("Can't access account's posts.")
    else:
        return HttpResponse("You must be authenticated to access this page.")
    return HttpResponse(request, "SocialSite/Post/Posts")


# Create Post Lists for existing accounts
def create_post_lists_job(request):
    user = request.user
    if user.is_authenticated and user.is_superuser:
        create_post_list_jobs(request)
    return HttpResponse("Success")


# Adds poster to all previously made posts
def add_accounts_to_posts_job(request):
    user = request.user
    if user.is_authenticated and user.is_superuser:
        add_user_to_posts(request)
    return HttpResponse("Success")


# Saves temporary profile in order to crop image
def save_temp_profile_image_from_base64String(imageString, user):
    INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
    try:
        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)
        if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
            os.mkdir(settings.TEMP + "/" + str(user.pk))
        url = os.path.join(f"{settings.TEMP}/{user.pk}", TEMP_PROFILE_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(imageString)
        with storage.open('', 'wb+') as destination:
            destination.write(image)
            destination.close()
        return url
    except Exception as e:
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            imageString += "=" * ((4 - len(imageString) % 4) % 4)
            return save_temp_profile_image_from_base64String(imageString, user)
    return None


# Crops profile image and saves
def crop_profile_image(request, *args, **kwargs):
    payload = {}
    user = request.user
    if request.POST and user.is_authenticated:
        try:
            imageString = request.POST.get("image")
            url = save_temp_profile_image_from_base64String(imageString, user)
            img = cv2.imread(url)

            cropX = int(float(str(request.POST.get("cropX"))))
            cropY = int(float(str(request.POST.get("cropY"))))
            cropWidth = int(float(str(request.POST.get("cropWidth"))))
            cropHeight = int(float(str(request.POST.get("cropHeight"))))
            if cropX < 0:
                cropX = 0
            if cropY < 0:
                cropY = 0
            crop_img = img[cropY:cropY + cropHeight, cropX:cropX + cropWidth]

            cv2.imwrite(url, crop_img)


            # delete the old image
            # if user.profile_image.name !=
            user.profile_image.delete()

            # Save the cropped image to user model
            user.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
            user.save()

            payload['result'] = "success"
            payload['cropped_profile_image'] = user.profile_image.url

            # delete temp file
            os.remove(url)

        except Exception as e:
            print("exception: " + str(e))
            payload['result'] = "error"
            payload['exception'] = str(e)
    return HttpResponse(json.dumps(payload), content_type="application/json")


# Create posts view with form management
def create_post_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    user_id = request.user.id
    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse("Something went wrong.")
    if account.pk != request.user.pk:
        return HttpResponse("You cannot post to someone else's profile.")

    context = {}
    context['defaultPostImage'] = settings.MEDIA_URL + 'media/defaultPostImage.png'
    if request.POST:
        form = PostCreationForm(request.POST)
        if form.is_valid():
            new_post = form.save()
            # new_comment_list = CommentList(post=new_post)
            if form.cleaned_data['is_image']:
                tempUrl = os.path.join(f"{settings.TEMP}/{request.user.id}", TEMP_POST_IMAGE_NAME)
                new_post_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9)) + ".png"
                new_post.image.save(new_post_name, files.File(open(tempUrl, 'rb')))

            try:
                postList = PostList.objects.get(user=request.user)
                postList.add_post(new_post)

            except PostList.DoesNotExist:
                return HttpResponse("Something went wrong")
            new_post.poster = account
            new_post.save()
            return redirect("view", user_id=account.pk)
        else:
            form = PostCreationForm(request.POST)
            context['form'] = form
    else:
        context['form'] = PostCreationForm()
    context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    return render(request, "SocialSite/Post/create_post.html", context)


# Saves temp post image
def save_temp_post_image_from_base64String(imageString, user):
    INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
    try:
        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)
        if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
            os.mkdir(settings.TEMP + "/" + str(user.pk))
        url = os.path.join(f"{settings.TEMP}/{user.pk}", TEMP_POST_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(imageString)
        with storage.open('', 'wb+') as destination:
            destination.write(image)
            destination.close()
        return url
    except Exception as e:
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            imageString += "=" * ((4 - len(imageString) % 4) % 4)
            return save_temp_post_image_from_base64String(imageString, user)
    return None

# Crops post image
def crop_post_image(request, *args, **kwargs):
    payload = {}
    user = request.user
    if request.POST and user.is_authenticated:
        try:
            imageString = request.POST.get("image")
            #TEMP_POST_IMAGE_NAME = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            url = save_temp_post_image_from_base64String(imageString, user)
            img = cv2.imread(url)

            cropX = int(float(str(request.POST.get("cropX"))))
            cropY = int(float(str(request.POST.get("cropY"))))
            cropWidth = int(float(str(request.POST.get("cropWidth"))))
            cropHeight = int(float(str(request.POST.get("cropHeight"))))
            if cropX < 0:
                cropX = 0
            if cropY < 0:
                cropY = 0
            crop_img = img[cropY:cropY + cropHeight, cropX:cropX + cropWidth]

            cv2.imwrite(url, crop_img)

            url = "../../../media/temp/" + str(user.id) + "/" + str(TEMP_POST_IMAGE_NAME)

            payload['result'] = "success"
            payload['tempCroppedImageUrl'] = url


            # delete temp file
            # os.remove(url)

        except Exception as e:
            print("exception: " + str(e))
            payload['result'] = "error"
            payload['exception'] = str(e)
    return HttpResponse(json.dumps(payload), content_type="application/json")

# Post view
def post_view(request, *args, **kwargs):
    context = {}
    user = request.user
    post_id = kwargs.get("post_id")
    user_id = kwargs.get("user_id")

    if user.is_authenticated:
        try:
            account = Account.objects.get(pk=user_id)
        except Account.DoesNotExist:
            return HttpResponse("Something went wrong")
        try:
            postList = PostList.objects.get(user=account)
        except PostList.DoesNotExist:
            return HttpResponse("PostList does not exist.")

        post = postList.posts.get(pk=post_id)
        if post:
            context['account_id'] = account.id
            context['post_id'] = post_id
            context['username'] = account.username
            context['profile_image'] = account.profile_image.url
            context['post_has_image'] = post.is_image
            if post.is_image:
                context['post_image'] = post.image.url
            context['text_content'] = post.text_content
            context['tagged_location'] = post.tagged_location
            context['created_at'] = post.created_at.date()
            context['num_of_likes'] = post.num_of_likes
            context['is_shared'] = post.is_shared_post

            if post.is_shared_post:
                context['shared_post'] = post.shared_post
            has_liked = False
            try:
                has_liked = post.usersWhoLiked.get(id=user.id)
                if has_liked:
                    context['has_liked'] = True
            except:
                context['has_liked'] = has_liked

            # Get accounts friend list
            # If it doesn't exist, make one
            try:
                friend_list = FriendList.objects.get(user=account)
            except FriendList.DoesNotExist:
                friend_list = FriendList(user=account)
                friend_list.save()
            friends = friend_list.friends.all()

            try:
                comment_list = CommentList.objects.get(post=post)
            except CommentList.DoesNotExist:
                comment_list = CommentList(post=post)
                comment_list.save()
            all_comments = comment_list.comments.all()
            comment_list = list(all_comments)
            comment_list.sort(key=lambda x: x.createdAt, reverse=True)
            context['comments'] = comment_list[0:3]

            if post.tagged_users:
                tagged_accounts = []
                tagged_users = post.tagged_users.split(', ')

                for tagged_user in tagged_users:
                    try:
                        tagged_account = Account.objects.get(username=tagged_user)
                        tagged_accounts.append(tagged_account)
                    except Account.DoesNotExist:
                        continue
                context['tagged_users'] = tagged_accounts

            # Set initial variables
            is_self = True
            is_friend = False
            # If user is logged in and is not viewing own profile
            if user != account:
                is_self = False
                # If user is friend of the account being viewed
                if friends.filter(pk=user.id):
                    is_friend = True

                # If user is not friends with account
                else:
                    is_friend = False

            # If user is not logged in
            elif not user.is_authenticated:
                is_self = False
            context['is_self'] = is_self
            context['is_friend'] = is_friend

        else:
            return HttpResponse("Post does not exist.")

    return render(request, "SocialSite/Post/post.html", context)

# Likes post
def like_post(request, *args, **kwargs):
    user = request.user
    if request.method == "POST" and user.is_authenticated:
        post_id = request.POST.get("post_id")
        if post_id:
            post = Post.objects.get(pk=post_id)
            if post:
                account = post.poster
                if account:
                    account_id = account.id
                    try:
                        has_liked = post.usersWhoLiked.get(id=user.id)
                        post.unlike_post(account)
                        return HttpResponse("Unlike Post.")
                    except:
                        post.like_post(account)
                        return HttpResponse("Liked Post.")
            else:
                return HttpResponse("Post doesn't exist.")
        else:
            return HttpResponse("Post doesn't exist.")
    else:
        return redirect("login")
    return HttpResponse("Post doesn't exist.")

# deletes post
def delete_post(request, *args, **kwargs):
    payload = {}
    user = request.user
    if request.method == "GET" and user.is_authenticated:
        post_id = kwargs.get("post_id")
        if post_id:
            try:
                post = Post.objects.get(pk=post_id)
            except Post.DoesNotExist:
                return HttpResponse("Something went wrong")
            try:
                account = Account.objects.get(id=user.id)
            except Account.DoesNotExist:
                return HttpResponse("Something went wrong")
            try:
                post_list = PostList.objects.get(user=account)
            except PostList.DoesNotExist:
                return HttpResponse("Something went wrong")
            has_post = post_list.posts.get(id=post_id)
            if has_post:
                if post:
                    try:
                        comment_list = CommentList.objects.get(post=post)
                    except CommentList.DoesNotExist:
                        return HttpResponse("Something went wrong")
                    comments = comment_list.comments.all()
                    for comment in comments:
                        comment.delete()
                    post.delete()
                    payload['response'] = "Deleted Post."
                    return redirect("view", user_id=user.id)

                else:
                    payload['response'] = "Something went wrong."
        else:
            payload['response'] = "Post_id not accessible."
    else:
        payload['response'] = "You must be authenticated to delete a post."
    return HttpResponse(json.dumps(payload), content_type="application/json")

# unlikes post
def unlike_post(request, *args, **kwargs):
    payload = {}
    user = request.user
    if request.method == "POST" and user.is_authenticated:
        post_id = request.POST.get("post_id")
        if post_id:
            post = Post.objects.get(pk=post_id)
            if post:
                post.unlike_post(user)
                payload['response'] = "Unliked Post."
                payload['num_of_likes'] = post.num_of_likes
            else:
                payload['response'] = "Something went wrong."
        else:
            payload['response'] = "Post_id not accessible."
    else:
        payload['response'] = "You must be authenticated to unlike a post."
    return HttpResponse(json.dumps(payload), content_type="application/json")


# Shares post
def share_post(request, *args, **kwargs):
    payload = {}
    user = request.user
    if request.method == "POST" and user.is_authenticated:
        post_id = request.POST.get("post_id")
        if post_id:
            post = Post.objects.get(pk=post_id)
            if post:
                post.share_post(user)
                payload['response'] = "Shared Post."
            else:
                payload['response'] = "Something went wrong."
        else:
            payload['response'] = "Post_id not accessible."
    else:
        payload['response'] = "You must be authenticated to share a post."
    return HttpResponse(json.dumps(payload), content_type="application/json")

# Make a comment view
def make_comment_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    user_id = request.user.id
    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse("Something went wrong.")
    context = {}
    if request.POST:
        post_id = kwargs.get("post_id")
        form = CommentCreationForm(request.POST)
        if form.is_valid():
            new_comment = form.save()
            try:
                post = Post.objects.get(pk=post_id)
            except Post.DoesNotExist:
                return HttpResponse("Post does not exist.")
            try:
                comment_list = CommentList.objects.get(post=post)
            except CommentList.DoesNotExist:
                comment_list = CommentList(post=post)
                comment_list.save()

            comment_list.add_comment(new_comment)
            new_comment.user = account
            new_comment.save()
            return redirect("post", user_id=post.poster.id, post_id=post_id)
        else:
            form = CommentCreationForm(request.POST)
            context['form'] = form
    else:
        context['form'] = CommentCreationForm()
    return render(request, "SocialSite/Post/make_comment.html", context)

# View post comments
def comments_view(request, *args, **kwargs):
    # make comment view
    # need to make view comment button on each post page
    context = {}
    user = request.user
    post_id = kwargs.get("post_id")
    if user.is_authenticated:
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return HttpResponse('Post does not exist.')
        try:
            post_comment_list = CommentList.objects.get(post=post)
        except PostList.DoesNotExist:
            post_comment_list = CommentList(post=post)
            post_comment_list.save()
        post_comments = post_comment_list.comments.all()
        comment_list = list(post_comments)
        comment_list.sort(key=lambda x: x.createdAt, reverse=True)
        context['comments'] = comment_list
        context['post_id'] = post_id
        if post.poster:
            context['poster_id'] = post.poster

    return render(request, "SocialSite/Post/comments.html", context)


# Edit post view with form
def edit_post_view(request, *args, **kwargs):
    user = request.user
    context = {}

    if not user.is_authenticated:
        return redirect("login")
    post_id = kwargs.get("post_id")
    try:
        post_list = PostList.objects.get(user=user)
    except PostList.DoesNotExist:
        return HttpResponse("User doesn't have a post list.")
    try:
        post = post_list.posts.get(id=post_id)
    except:
        return HttpResponse("That is not a post on your post list.")
    if request.POST:
        form = PostUpdateForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("post", user_id=user.id, post_id=post.id)
        else:
            form = PostUpdateForm(request.POST, instance=post,
                                  initial={
                                      "post_image": post.image.url,
                                      "text_content": post.text_content,

                                  }
                                  )
            context['form'] = form
    else:
        form = PostUpdateForm(
            initial={
                "post_image": post.image.url,
                "text_content": post.text_content,

            }
        )
        context['form'] = form
    return render(request, "SocialSite/Post/edit_post.html", context)