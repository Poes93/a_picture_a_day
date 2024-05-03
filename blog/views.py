from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import generic, View
from django.db.models import Q
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from .models import Post, Comment
from .forms import CommentForm, PostForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.db import IntegrityError, transaction
from django.contrib import messages

class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(status=1).order_by("-created_on")
    template_name = "index.html"
    paginate_by = 8

class PostDetail(View):
    def get(self, request, slug):
        # Begin with a base query that includes only published posts
        queryset = Post.objects.filter(status=1)
        
        # If the user is authenticated, adjust the queryset to also include their own drafts
        if request.user.is_authenticated:
            queryset = Post.objects.filter(Q(status=1) | Q(author=request.user, status=0))
        
        # Attempt to get the post with the slug, within the refined queryset
        post = get_object_or_404(queryset, slug=slug)

        # Gather comments and like status for the post
        comments = post.comments.order_by('-created_on')
        liked = post.likes.filter(id=request.user.id).exists() if request.user.is_authenticated else False

        return render(
            request,
            'post_detail.html',
            {
                'post': post,
                'comments': comments,
                'commented': False,
                'liked': liked,
                'comment_form': CommentForm(),
            }
        )


    @method_decorator(login_required)
    def post(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter().order_by('-created_on')
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()

        else:
            comment_form = CommentForm()

        return render(
            request,
            'post_detail.html',
            {
                'post': post,
                'comments': comments,
                'commented': True,
                'liked': liked,
                'comment_form': CommentForm(),
            }
        )

class PostLike(View):
    @method_decorator(login_required)
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))

class UserPostsView(LoginRequiredMixin, generic.ListView):
    model = Post
    template_name = "user_posts.html"
    paginate_by = 8

    def get_queryset(self):
        # Retrieve the filter from the URL parameter, default to showing all posts
        post_status = self.request.GET.get('status', 'all')

        if post_status == 'published':
            return Post.objects.filter(author=self.request.user, status=1).order_by("-created_on")
        elif post_status == 'drafts':
            return Post.objects.filter(author=self.request.user, status=0).order_by("-created_on")
        else:
            return Post.objects.filter(author=self.request.user).order_by("-created_on")


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "post_create.html"

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        # Use the 'status' field directly from the form
        # Assuming 'status' is a choice field in your form where 'draft' and 'publish' are possible values
        status = form.cleaned_data['status']
        if status == 'publish':
            post.status = 1  # Assuming 1 is for published
        else:
            post.status = 0  # Assuming 0 is for drafts

        try:
            with transaction.atomic():
                post.save()  # This will now handle transaction rollback on error
                return HttpResponseRedirect(post.get_absolute_url())
        except IntegrityError as e:
            messages.error(self.request, "There was an error saving your post. Please try again.")
            return self.form_invalid(form)

        return HttpResponseRedirect(post.get_absolute_url())


class PostUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Post
    form_class = PostForm
    template_name = "post_edit.html"

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()
        post_detail_url = reverse('post_detail', kwargs={'slug': post.slug})
        return redirect(post_detail_url)

class PostDelete(LoginRequiredMixin, generic.DeleteView):
    model = Post
    template_name = "post_delete.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('user_posts')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return HttpResponseRedirect(referer)
        return HttpResponseRedirect(success_url)

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('post_detail', slug=comment.post.slug)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('post_detail', slug=comment.post.slug)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'comment_edit.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_slug = comment.post.slug
    if request.user == comment.author:
        comment.delete()
        return redirect('post_detail', slug=post_slug)
    else:
        return redirect('post_detail', slug=post_slug)
