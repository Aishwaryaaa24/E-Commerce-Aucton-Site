from unicodedata import category
from django.contrib.auth.models import AbstractUser
from django.db import models

from django.core.files.storage import FileSystemStorage

import auctions

fs = FileSystemStorage(location='images', base_url='/media/images')

# The FileSystemStorage class implements basic file storage on a local filesystem. 
# It inherits from Storage and provides implementations for all the public methods thereof.

# location parameter gives the relative location path to store/upload image files(if not mentioned, takes MEDIA_ROOT (from seetings.py) as its default path)

# base_url parameter gives the relative url from where the image is supposed to be rendered(if not mentioned, takes MEDIA_URL (from seetings.py) as its default url)

class User(AbstractUser):
    pass

class Category(models.Model):
    def __str__(self):
        return f"{self.cat_name}"
    cat_name = models.CharField(max_length=64)

class AuctionListing(models.Model):
    def __str__(self):
        return f"{self.item_name}"

    item_name = models.CharField(max_length=64)
    content = models.CharField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name="itemsByCategory")
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="person")
    start_bid = models.DecimalField(max_digits=6, decimal_places=2)
    img = models.ImageField(storage = fs)
    is_active = models.BooleanField(default=True)
    won_by = models.ForeignKey(User, on_delete=models.CASCADE, default=None , blank=True, null=True)

class Comment(models.Model):
    def __str__(self):
        return f"Comment by: {self.name}"
    name = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comm")
    content = models.CharField(max_length=500)
    item = models.ForeignKey(AuctionListing,on_delete=models.CASCADE)

class Bid(models.Model):
    def __str__(self):
        return f"{self.val}"
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    val = models.DecimalField(max_digits=6, decimal_places=2)
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="list_items")
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

