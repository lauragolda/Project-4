from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json

from .models import Like, Post, User, Follow


def index(request):
    allposts = Post.objects.all().order_by("id").reverse()
    paginator = Paginator(allposts, 10)
    pageNumber = request.GET.get('page')
    posts = paginator.get_page(pageNumber)

    allLikes = Like.objects.all()

    likedPosts = []
    try:
        for like in allLikes:
            if like.user.id == request.user.id:
                likedPosts.append(like.post.id)
    except:
        likedPosts = []

    return render(request, "network/index.html",{
        "allposts":allposts,
        "posts":posts,
        "likedposts":likedPosts
    })
    


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
    

def newPost(request):
    if request.method == "POST":
        content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        post = Post(content=content, author=user)
        post.save()
        return HttpResponseRedirect(reverse(index))
    
def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    allposts = Post.objects.filter(author=user).order_by("id").reverse()
    paginator = Paginator(allposts, 10)
    pageNumber = request.GET.get('page')
    posts = paginator.get_page(pageNumber)

    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(followedUser=user)

    try:
        checkFollow = followers.filter(user=User.objects.get(pk=request.user.id))
        if len(checkFollow) != 0:
            isFollowing = True
        else:
            isFollowing = False
    except:
        isFollowing=False

    return render(request, "network/profile.html",{
        "allposts":allposts,
        "posts":posts,
        "username":user.username,
        "following": following,
        "followers": followers,
        "isFollowing": isFollowing,
        "user_profile": user
    })

def follow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    userfollowData = User.objects.get(username=userfollow)
    f = Follow(user=currentUser, followedUser=userfollowData)
    f.save()
    user_id = userfollowData.id

    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))


def unfollow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    userfollowData = User.objects.get(username=userfollow)
    f = Follow.objects.get(user=currentUser, followedUser=userfollowData)
    f.delete()
    user_id = userfollowData.id

    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))

def following(request):
    currentUser = User.objects.get(pk=request.user.id)
    followingPeople = Follow.objects.filter(user=currentUser)
    allPosts = Post.objects.all().order_by('id').reverse()
    followingPosts = []
    
    allLikes = Like.objects.all()
    likedPosts = []
    try:
        for like in allLikes:
            if like.user.id == request.user.id:
                likedPosts.append(like.post.id)
    except:
        likedPosts = []

    for post in allPosts:
        for person in followingPeople:
            if person.followedUser == post.author:
                followingPosts.append(post)

    paginator = Paginator(followingPosts, 10)
    pageNumber = request.GET.get('page')
    posts = paginator.get_page(pageNumber)

    return render(request, "network/following.html",{
        "posts":posts,
        "likedposts":likedPosts
    })

def edit(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        editPost = Post.objects.get(pk=post_id)
        editPost.content = data["content"]
        editPost.save()
        return JsonResponse({"message": "Post was edited!", "data": data["content"]})
    
def remove_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like.objects.filter(user=user, post=post)
    like.delete()
    return JsonResponse({"message": "You unliked this post!"})
    

def add_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    newLike = Like(user=user, post=post)
    newLike.save()
    return JsonResponse({"message": "You liked this post!"})

    
