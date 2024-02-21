from django.shortcuts import render, get_object_or_404, reverse
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

    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter().order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )

    def post(self, request, slug, *args, **kwargs):

        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter().order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
        else:
            comment_form = CommentForm()

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                "comment_form": comment_form,
                "liked": liked
            },
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
