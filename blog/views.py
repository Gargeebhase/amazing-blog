from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from .models import Post,Comment
from django.utils import timezone
from .forms import PostForm,CommentForm, SignUpForm, SearchForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def post_list(request):
    if request.method == 'POST':
        search = SearchForm(request.POST)
        if search.is_valid():
            searchtag = search.cleaned_data.get('searchitem')
            posts = Post.objects.filter(text__contains=searchtag)
    else:    
        posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    form = SearchForm()
    return render(request, 'blog/post_list.html', {'posts':posts, 'form':form} )

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post).order_by('created_date')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment= form.save(commit=False)
            comment.post = post
            comment.created_date = timezone.now()
            comment.save()
    else:
        form = CommentForm()
    return render(request, 'blog/post_detail.html', {'post': post,'form':form, 'comments':comments})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.birth_date = form.cleaned_data.get('birth_date')
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('post_list')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
