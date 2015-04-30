from django.db import models

# User class for built-in authentication module
from django.contrib.auth.models import User
from django.utils import timezone
import time, datetime
        
class UserInfo(models.Model):
    # Use Django forms
    # username = models.CharField(max_length=50)
    user = models.ForeignKey(User) # stores additional info such as username, email
    show_email = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to="user-icons",blank=True,default="") # optional avatar that can be uploaded
    phone = models.CharField(max_length=12, default="", blank=True) # optional phone number
    num_ratings = models.IntegerField(default=0)    # number of users who have rated this user
    total_rating = models.IntegerField(default=0.0)   # sum of all ratings
    average_rating = models.FloatField(default=0.0) # average rating (num_ratings/total_rating), for convenience
    def __unicode__(self):
        return self.user.username
    
    def get_username(self):
      return self.user.username

class UserComment(models.Model):
    class Meta:
        ordering = ['-time'] # when collected together in a set, comments will be organized by time (most recent first)
        
    subject = models.ForeignKey(User, related_name="subject")  # user that this comment is about
    author = models.ForeignKey(User, related_name="author")  # user that made this comment
    text = models.CharField(max_length=500,default="")      # content of the comment
    time = models.DateTimeField(auto_now_add=True)

class SaleItem(models.Model):
    class Meta:
        ordering = ['expiration_date'] # when collected together in a set, comments will be organized by expiration date (freshest first)
        
    seller = models.ForeignKey(UserInfo)  # user selling the item
    name = models.CharField(max_length=255,default="") # general name (e.g., "Eggs")
    brand = models.CharField(max_length=255, blank=True,default="") # optional
    quantity = models.CharField(max_length=255,default="") # can be more than just a number (e.g., "12 oz.")
    description = models.CharField(max_length=500, blank=True,default="") # optional
    price = models.DecimalField(max_digits=5, decimal_places=2) # up to $999.99
    purchase_date = models.DateField(blank=True,null=True) # optional
    expiration_date = models.DateField(default=timezone.now) # date for item tracking/deletion if time runs out
    picture = models.ImageField(upload_to="item-pictures",null=True) # required!
    posted_time = models.DateTimeField(auto_now_add=True)

class Offer(models.Model):
    sender = models.ForeignKey(User, related_name="sender")       # the person offering
    recipient = models.ForeignKey(User, related_name="recipient") # the person who is receiving the offer
    item = models.ForeignKey(SaleItem,null=True)  # the item the offer is about