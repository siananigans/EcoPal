from django.db import models
from django.contrib.auth.models import User

class Saved_search(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    result = models.TextField(blank=True)
