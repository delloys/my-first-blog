from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post, Comment, Profile, User
from .forms import PostForm,CommentForm, ProfileForm, UserForm
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

# Create your views here.

def profile_edit(request,pk):
    profile_info = get_object_or_404(Profile, pk=pk)
    user_info = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        # Комментарий был опубликован
        profile_form = ProfileForm(request.POST, request.FILES)
        user_form = UserForm(data=request.POST)
        if profile_form.is_valid():
            update_profile = profile_form.save(commit=False)
            update_profile.user_id = request.user.id
            update_profile.save()
        if user_form.is_valid():
            user_info.first_name = user_form.cleaned_data['first_name']
            user_info.last_name = user_form.cleaned_data['last_name']
            user_info.email = user_form.cleaned_data['email']
            user_info.save()
        return redirect('profile_detail', pk=pk)
    else:
        profile_form = ProfileForm(initial={'status':profile_info.status})
        user_form = UserForm(initial={'first_name':profile_info.user.first_name,'last_name':profile_info.user.last_name,'email':profile_info.user.email})
    return render(request,'blog/profile_edit.html', {'profile_info':profile_info,'profile_form':profile_form, 'user_form':user_form})

def profile_detail(request,pk):
    profile_info = get_object_or_404(Profile, pk=pk)
    posts = Post.objects.filter(author=request.user.id)
    return render(request,'blog/profile_detail.html', {'profile_info': profile_info,'posts':posts})

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    dict = {}
    for i in range(len(posts)):
        dict[posts[i].title] =len(posts[i].comments.filter(active=True))
    return render(request, 'blog/post_list.html', {'posts': posts,'dict_comm': dict})

def post_delete(request,pk):
    Post.objects.filter(pk=pk).delete()
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request,'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Список активных комментариев к этой записи
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        # Комментарий был опубликован
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создайте объект Comment, но пока не сохраняйте в базу данных
            new_comment = comment_form.save(commit=False)
            new_comment.name = request.user.username
            # Назначить текущий пост комментарию
            new_comment.post = post
            print(new_comment.post, 'nc')
            # Сохранить комментарий в базе данных
            new_comment.save()

    else:
        comment_form = CommentForm()
    return render(request,
                  'blog/post_detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form})

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
    return render(request, 'blog/post_new.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        kwargs = request.user
        print(kwargs, 'mew', post.author)
        if form.is_valid():
            if post.author == request.user:
                post = form.save(commit=False)
                post.author = request.user
                post.published_date = timezone.now()
                post.save()
                return redirect('post_detail', pk=post.pk)
            else:
                return redirect('/', pk=post.pk)

    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_edit.html', {'form': form})