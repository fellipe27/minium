from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    birthday = models.DateField(null=True, blank=True)
    picture = models.BinaryField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    following = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='followers')

    def follow(self, user):
        self.following.add(user)

    def unfollow(self, user):
        self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(id=user.id).exists()

    def __str__(self):
        return self.username
