import re
from unicodedata import decimal
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Category, User,AuctionListing,Comment, Bid, Watchlist


def index(request):
    listings = AuctionListing.objects.all()
    cats = Category.objects.all()
    bids = Bid.objects.all()
    return render(request, "auctions/index.html", {
        "listings" : listings,
        "bid" : bids,
        # "price" : Bid.val
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def create(request):
    alert = 0
    if request.method == "POST":
        alert = 1
        name = request.POST.get("title")
        content = request.POST.get("content")
        startbid = request.POST.get("startbid")
        category = request.POST.get("category")
        img = request.FILES.get("image")
        # print(name is not None and content is not None and startbid is not None and img is not None)
        # print(img)
        if name is not None and content is not None and startbid is not None and img is not None:
            curr_cat,created = Category.objects.get_or_create(cat_name = category.capitalize())
            AuctionListing.objects.create(item_name = name, content = content , category = curr_cat , listed_by  = request.user , start_bid = startbid, img = img)
            # print("listing created")
            createdlisting = AuctionListing.objects.get(item_name = name , listed_by  = request.user)
            Bid.objects.create(item = createdlisting, val = startbid, person = request.user)
            # curr_bid = Bid.objects.get(item = createdlisting, val = startbid, person = request.user)
        else:
            alert = 2
            #alert dedo
    return render(request,"auctions/create.html",{
        "alert" : alert,
    })

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def listing(request, listing_id):
    listingdeets = AuctionListing.objects.get(pk = listing_id) # obj of current listing
    cat =  listingdeets.category
    to_close = request.POST.get('close')
    lower_bid = 2
    is_comment = request.POST.get('comment')
    can_close = False
    is_in_watchlist = 2
    signed_in = 2
    if to_close == 'Close Auction':
        listingdeets.is_active = False
        listingdeets.save()
    if listingdeets.listed_by == request.user and listingdeets.is_active ==  True:
        can_close = True
    # list_instance = Watchlist.objects.filter(user = request.user, item = listingdeets).first() ==> #obj of watchlist of that listing item and user
    if request.method == "POST":
        bid = request.POST.get('mybid')
        val = request.POST.get('checkbox')
        is_comment = request.POST.get('comment')
        print("is comment : ", is_comment)
        if val == 'Add':
            Watchlist.objects.create(user = request.user, item = listingdeets)
        elif val == 'Remove':
            Watchlist.objects.filter(user = request.user, item = listingdeets).delete()
        elif val == 'Place Bid':
            if float(bid) <= listingdeets.start_bid:
                lower_bid = 1
            else:
                lower_bid = 0
                Bid.objects.create(item = listingdeets ,val = bid , person = request.user)
                listingdeets.start_bid = bid
                listingdeets.save()
                listingdeets.won_by = request.user
                listingdeets.save()
    if request.user.is_authenticated:
        watchlist = Watchlist.objects.filter(user = request.user, item = listingdeets).first()
        if watchlist == None:
            is_in_watchlist = 0
        else:
            is_in_watchlist = 1
    filtered_bid = Bid.objects.filter(item = listingdeets)
    if not filtered_bid:
        Bid.objects.create(item = listingdeets ,val = listingdeets.start_bid , person = request.user)
        filtered_bid = Bid.objects.filter(item = listingdeets)
        
    temp_bid = filtered_bid.order_by('-val')[0]
    curr_bid = temp_bid.val 
    curr_user = request.user
    if curr_user.id == None :
        signed_in = 0
    else:
        signed_in = 1
    # if signed in user adds comments
    all_comments = Comment.objects.filter(item = listingdeets)
    if signed_in == 1:
        print("signed in")
        if is_comment == 'Place Comment':
            print("entered if loop")
            cont = request.POST.get('comment_content')
            Comment.objects.create(name = request.user, content = cont , item = listingdeets)
            print("comment created")
        elif is_comment == 'Cancel':
             return render(request,"auctions/listing.html",{
            "listingdeets" : listingdeets,
            "is_in_watchlist" : is_in_watchlist,
            "lower_bid" : lower_bid,
            "curr_bid" : curr_bid,
            "cat" : cat,
            "can_close" : can_close,
            "curr_user" : curr_user,
            "signed_in ": signed_in,
            "commentsForListing" : all_comments,
        }) 
    return render(request,"auctions/listing.html",{
        "listingdeets" : listingdeets,
        "is_in_watchlist" : is_in_watchlist,
        "lower_bid" : lower_bid,
        "curr_bid" : curr_bid,
        "cat" : cat,
        "can_close" : can_close,
        "curr_user" : curr_user,
        "signed_in ": signed_in,
        "commentsForListing" : all_comments,
    })
def watchlist(request):
    watchlist_items = Watchlist.objects.filter(user = request.user)
    
    return render(request, "auctions/watchlist.html",{
        "watchlist_items" : watchlist_items,
    })
def categories(request):
    cats = Category.objects.all()
    return render(request,"auctions/cat.html",{
        "cats" : cats,
    })
def idx(request , cat_id):
    cat_obj = Category.objects.get(id = cat_id)
    item_list = cat_obj.itemsByCategory.all()
    return render(request, "auctions/listByCat.html",{
        "item_list" : item_list,
    })