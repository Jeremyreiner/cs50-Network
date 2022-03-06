from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.db.models import OuterRef, Count
from django.core.paginator import Paginator


from django.views.decorators.csrf import csrf_exempt
import json

from .forms import NewPostForm
from .models import User, Like, Post, Follower


def index(request):
    if request.user.is_authenticated:
        user = request.session['_auth_user_id']
        likes = Like.objects.filter(post=OuterRef('id'), user_id = user)
        posts = Post.objects.filter().order_by('-post_date')
    else:
        posts = Post.objects.order_by('-post_date').all()
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': page_obj,
        'new_post': NewPostForm(),
    }
    return render(request, "network/index.html", context)


def new_post(request):
    form = NewPostForm(request.POST)
    
    if form.is_valid():
        user = User.objects.get(id=request.session['_auth_user_id'])
        text = form.cleaned_data['post_text']
        post = Post(user=user,text=text)
        post.save()
        return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('index'))


@csrf_exempt
def edit(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("post") is not None:
            post.text = data["post"]
        post.save()
        return HttpResponse(status=204)


def profile(request, username):
    following = 0
    profiles_user = User.objects.get(username=username)
    if request.user.is_authenticated:
        logged_in = request.session['_auth_user_id']
        following = Follower.objects.filter(follower=logged_in, following=profiles_user).count()
        like = Like.objects.filter(post=OuterRef('id'), user_id= logged_in)
        posts = Post.objects.filter(user=profiles_user).order_by('-post_date').annotate(current_like=Count(like.values('id')))
        if following >= 1:
            result = 'Unfollow'
        else: 
            result = 'Follow'
    else:
        posts = Post.objects.filter(user=profiles_user).order_by('-post_date')  

    total_followers = Follower.objects.filter(following=profiles_user).count()
    total_following = Follower.objects.filter(follower=profiles_user).count()
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'user_profile':profiles_user, 
        'posts':page_obj, 
        'following': following, 
        'total_followers':total_followers,
        'total_following': total_following,
        'new_post': NewPostForm(), 
        'result': result
    }
    return render(request, 'network/profile.html', context)


def like(request, id):
    css = 'fas fa-heart'
    user = User.objects.get(id=request.session['_auth_user_id'])
    post = Post.objects.get(id=id)
    like = Like.objects.get_or_create(user=user, post=post)

    if not like[1]:
        css = 'far fa-heart'
        Like.objects.filter(user=user, post=post).delete()

    total_likes = Like.objects.filter(post=post).count()
    
    context = {
        'like': id,
        'css_marker':  css,
        'total_likes': total_likes
    }
    return JsonResponse(context)


def follow(request, id):
    result = 'follow'
    user = User.objects.get(id = request.session['_auth_user_id'])
    following_user = User.objects.get(id=id)
    follower = Follower.objects.get_or_create(follower=user, following=following_user)

    if not follower[1]:
        Follower.objects.filter(follower=user, following=following_user).delete()
        result = 'unfollow'
    
    total_followers = Follower.objects.filter(following=following_user).count()
    context = {
        'result': result,
        'total_followers': total_followers
    }
    return JsonResponse(context)


def following(request):
    user = request.session['_auth_user_id']
    followers = Follower.objects.filter(follower=user)
    posts = Post.objects.filter(user_id__in=followers.values('following_id').order_by('-id'))

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': page_obj,
        'new_post': NewPostForm()
    }
    return render(request, 'network/following.html', context)


#------------login/register ---------------------
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
