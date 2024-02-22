from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from .models import Post, Comment
from .forms import CommentForm, PostForm


class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(status=1).order_by("-created_on")
    template_name = "index.html"
    paginate_by = 8


class PostDetail(View):

    def get(self, request, slug):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter().order_by('-created_on')
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

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
            new_comment.author = request.user  # Set the comment's author as the current user
            new_comment.post = post  # Assuming you have the post object already
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

    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class UserPostsView(generic.ListView):
    model = Post
    template_name = "user_posts.html"
    paginate_by = 8

    def get_queryset(self):
        queryset = Post.objects.filter(author=self.request.user, status=1).order_by("-created_on")
        return queryset


# User can only post once every 24 hours
class PostCreate(generic.CreateView):
    model = Post
    form_class = PostForm
    template_name = "post_create.html"

    def form_valid(self, form):
        try:
            post = form.save(commit=False)
            post.author = self.request.user
            action = self.request.POST.get('action', 'Draft')

            if action == 'Publish':
                post.status = 1
            else:
                post.status = 0

            post.save()  # This might raise ValidationError
            return HttpResponseRedirect(post.get_absolute_url())
        except ValidationError as e:
            # Add the error from the ValidationError to the form
            form.add_error(None, e)
            return self.form_invalid(form)  # Re-render the form with errors


class PostUpdate(generic.UpdateView):
    model = Post
    form_class = PostForm
    template_name = "post_edit.html"

    def form_valid(self, form):
        # Get the post object
        post = form.save(commit=False)
        # Save any modifications to the post
        post.save()

        # Construct the URL for the post detail page
        post_detail_url = reverse('post_detail', kwargs={'slug': post.slug})

        # Redirect the user to the post detail page
        return redirect(post_detail_url)


class PostDelete(generic.DeleteView):
    model = Post
    template_name = "post_delete.html"
    pk_url_kwarg = 'pk'

    def get_success_url(self):
        # Redirect to the user's posts
        return reverse('user_posts')


class CommentEdit(generic.UpdateView):
    model = Comment
    fields = ['body']
    template_name = "comment_edit.html"
    pk_url_kwarg = 'comment_pk'

    def get_success_url(self):
        # Redirect to the post detail
        return reverse('post_detail', args=[self.object.post.slug])


def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        # Redirect or show error if the user is not the author of the comment
        return redirect('post_detail', slug=comment.post.slug)  # Adjust redirection as needed

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('post_detail', slug=comment.post.slug)  # Adjust redirection as needed
    else:
        form = CommentForm(instance=comment)

    return render(request, 'comment_edit.html', {'form': form, 'comment': comment})


def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_slug = comment.post.slug  # Remember the slug of the post to which the comment belongs
    if request.user == comment.author:
        comment.delete()
        # Redirect to the post detail page after deletion
        return redirect('post_detail', slug=post_slug)
    else:
        # Add your error handling here (e.g., setting a message, redirecting elsewhere)
        return redirect('post_detail', slug=post_slug)
