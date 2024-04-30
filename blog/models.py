from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from cloudinary.models import CloudinaryField
from django.urls import reverse
from django.utils.text import slugify
import uuid

class Post(models.Model):
    HAPPY = '😊'
    SAD = '😢'
    EXCITED = '🤩'
    ANGRY = '😠'
    LOVE = '❤️'
    SLEEPY = '😴'
    SURPRISED = '😮'
    CONFUSED = '😕'
    LAUGHING = '😂'
    NERVOUS = '😬'

    MOOD_CHOICES = [
        (HAPPY, 'Happy 😊'),
        (SAD, 'Sad 😢'),
        (EXCITED, 'Excited 🤩'),
        (ANGRY, 'Angry 😠'),
        (LOVE, 'Love ❤️'),
        (SLEEPY, 'Sleepy 😴'),
        (SURPRISED, 'Surprised 😮'),
        (CONFUSED, 'Confused 😕'),
        (LAUGHING, 'Laughing 😂'),
        (NERVOUS, 'Nervous 😬'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    featured_image = CloudinaryField('image')
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    mood = models.CharField(max_length=50, choices=MOOD_CHOICES, default=HAPPY)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(
        choices=[(0, "Draft"), (1, "Publish")],
        default=1
    )
    likes = models.ManyToManyField(
        User,
        related_name='blogpost_like',
        blank=True
    )

    class Meta:
        ordering = ["-created_on"]

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a slug from the title or use UUID if the title is empty
            self.slug = slugify(self.title) if self.title else uuid.uuid4().hex
        # Ensure the slug is unique
        original_slug = self.slug
        iteration = 1
        while Post.objects.filter(slug=self.slug).exists():
            self.slug = f"{original_slug}-{iteration}"
            iteration += 1
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return f"Comment {self.body} by {self.name}"

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.post.slug})
