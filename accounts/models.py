from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, blank=False)
    birthday = models.DateField(null=True, blank=True)
    picture = models.BinaryField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)