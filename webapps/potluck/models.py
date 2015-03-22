from django.db import models

# User class for built-in authentication module
from django.contrib.auth.models import User
import time
import datetime

# Create your models here.

class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.CharField(max_length=255)
    def __unicode__(self):
        fulltext = self.quantity + " " + self.name
        return fulltext

class Recipe(models.Model):
    name = models.CharField(max_length=140)
    user = models.ForeignKey(User, related_name="user")
    ingredients = models.ManyToManyField(Ingredient)
    def __unicode__(self):
        fulltext = self.user.username + ": " + self.grumbl
        return fulltext

class SaleItem(models.model):
    ingredient = models.ForeignKey(Ingredient) # ? Foreign Key?
    price = models.DecimalField(max_digits=5, decimal_places=2) # up to $999.99
    seller = models.ForeignKey(UserInfo)
    expiration_date = models.DateTimeField()

class Offer(models.Model):
    sender = models.ForeignKey(User, related_name="sender")
    recipient = models.ForeignKey(User, related_name="recipient")
    time = models.DateTimeField()
    location = models.CharField(max_length=255)
        
class UserInfo(models.Model):
    # Use Django forms
    # username = models.CharField(max_length=50)
    user = models.ForeignKey(User)
    avatar = models.ImageField(upload_to="user-icons",blank=True,default="")
    home = models.CharField(max_length=255, default="", blank=True)
    def __unicode__(self):
        return self.user.username
    
    def get_username(self):
      return self.user.username