from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User


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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = CloudinaryField('image')
    caption = models.CharField(max_length=255)
    text = models.TextField()
    mood = models.CharField(max_length=50, choices=MOOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s post on {self.created_at.strftime('%Y-%m-%d')}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')  # Prevents duplicate follow instances

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"


class Notification(models.Model):
    # Define different types of notifications
    FOLLOW = 'follow'
    LIKE = 'like'
    COMMENT = 'comment'
    POST = 'post'
    NOTIFICATION_TYPES = (
        (FOLLOW, 'Follow'),
        (LIKE, 'Like'),
        (COMMENT, 'Comment'),
        (POST, 'Post'),
    )

    # Notification fields
    to_user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.to_user.username} - {self.notification_type}"


def follow_user(request, user_id):
    user_to_follow = User.objects.get(pk=user_id)
    _, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
    if created:
        Notification.objects.create(
            to_user=user_to_follow,
            from_user=request.user,
            notification_type=Notification.FOLLOW
        )
    return HttpResponseRedirect(reverse('user_profile', args=[user_id]))
