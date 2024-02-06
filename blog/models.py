from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cloudinary.models import CloudinaryField


STATUS = ((0, "Draft"), (1, "Published"))


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
    photo = models.ImageField(upload_to='post_photos/', blank=True, null=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)
    mood = models.CharField(max_length=50, choices=MOOD_CHOICES, default=HAPPY)
    updated_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["created_on"]
    
    def __str__(self):
        return f"{self.title} | written by {self.author} | {self.created_on}"


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="commenter")
    body = models.TextField()
    approved = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return f"Comment {self.body} by {self.author}"
