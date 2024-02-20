from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from cloudinary.models import CloudinaryField
from django.urls import reverse
from django.utils.text import slugify


# post model
class Post(models.Model):
    HAPPY = '😊'
    SAD = '😢'
    EXCITED = '🤩'
    ANGRY = '😠'
    LOVE = '❤️'

    MOOD_CHOICES = [
        (HAPPY, 'Happy 😊'),
        (SAD, 'Sad 😢'),
        (EXCITED, 'Excited 🤩'),
        (ANGRY, 'Angry 😠'),
        (LOVE, 'Love ❤️'),
    ]

    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    featured_image = CloudinaryField('image', default='placeholder')
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    mood = models.CharField(max_length=50, choices=MOOD_CHOICES , default=HAPPY)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=[(0, "Draft"), (1, "Publish")], default=0)
    likes = models.ManyToManyField(User, related_name='blogpost_like', blank=True)

    class Meta:
        ordering = ["-created_on"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Prevent a user from posting more than once every 24 hours
        if not self.pk:  # Checking if the post is new
            last_post = Post.objects.filter(author=self.author).order_by('-created_on').first()
            if last_post and timezone.now() - last_post.created_on < timedelta(days=1):
                raise ValidationError('You can only post "A Photo a day".')
        
        super(Post, self).save(*args, **kwargs)


    def __str__(self):
        return self.title

    def number_of_likes(self):
        return self.likes.count()

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})


# Comment model
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)#

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return f"Comment {self.body} by {self.name}"

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.post.slug})


# user profile model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    # Add any other fields you need for the user profile

    def __str__(self):
        return self.user.username + "'s Profile"
