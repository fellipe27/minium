from django.db import models
from django.utils import timezone
from accounts.models import User
import uuid

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    story = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    picture = models.BinaryField(null=True, blank=True)
    claps = models.ManyToManyField(User, related_name='claps', blank=True)

    def like_post(self, user):
        self.claps.add(user)

    def unlike_post(self, user):
        self.claps.remove(user)

    def claps_amount(self):
        return self.claps.count()

    def user_liked_post(self, user):
        return self.claps.filter(id=user.id).exists()

    def __str__(self):
        return self.title

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return self.content
