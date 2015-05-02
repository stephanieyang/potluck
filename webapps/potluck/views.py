from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.db import transaction

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from potluck.forms import *
from potluck.models import *

from django.http import HttpResponse, Http404
from mimetypes import guess_type

# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator

# Used to send mail from within Django
from django.core.mail import send_mail

import datetime
from datetime import date

@login_required
def home(request):
    context = {}
    user_info = get_object_or_404(UserInfo,user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    context['user_info'] = user_info
    purge_old_items()
    return render(request, 'index.html', context)
    
def purge_old_items():
    items = SaleItem.objects.all()
    today = date.today()
    old_items = SaleItem.objects.filter(expiration_date__lt=today)
    old_items.delete()
    
@login_required
def buy(request): # DONE?
    context = {}
    user_info = get_object_or_404(UserInfo, user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    context['user_info'] = user_info
    # for now, display items put up for sale in the past week
    current_time = datetime.datetime.now()
    #past_week = current_time - datetime.timedelta(7,0,0,0,0,0) # subtract difference of 1 week
    items = SaleItem.objects.all()
    context['items'] = get_rows(items)
    # not the best notation, but better for consistency in the event anyone but me actually edits this
    return render(request, 'buy.html', context)

def get_rows(item_set):
    items_per_row = 3 # magic number
    full_item_list = list(item_set)
    rows = [full_item_list[i:i+items_per_row] for i in xrange(0,len(full_item_list),items_per_row)]
    return rows

@login_required
def delete_item(request, id): 
    print "delete_item: start"
    context = {}
    user_info = get_object_or_404(UserInfo, user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    item = get_object_or_404(SaleItem, id=id)
    #item = SaleItem.objects.get(id=id)
    context['user_info'] = user_info
    context['item'] = item
    item.delete()
    return redirect('/potluck/my_account/#tab-2', context)

@login_required
def edit_sale(request, id): # DONE
    context = {}
    user_info = get_object_or_404(UserInfo, user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    item = get_object_or_404(SaleItem,id=id)
    #item = SaleItem.objects.get(id=id)
    context['user_info'] = user_info
    context['item'] = item
    
    # if a get request, just return the form
    if request.method == 'GET':
      context['form'] = EditSaleForm()
      return render(request, 'edit-sale.html', context)
    
    # POST request - edit information
    form = EditSaleForm(request.POST, request.FILES)
    if not form.is_valid():
      print "edit_sale: invalid form", form.errors
      context['form'] = form
      return render(request, 'edit-sale.html', context)
    item.brand = form.cleaned_data['brand']
    item.quantity = form.cleaned_data['quantity']
    item.description = form.cleaned_data['description']
    item.price = form.cleaned_data['price']
    item.purchase_date = form.cleaned_data['purchase_date']
    item.expiration_date = form.cleaned_data['expiration_date']
    if 'picture' in request.FILES:
      item.picture = request.FILES['picture']
    item.save()
    return render(request, 'edit-sale.html', context)


def rate_user(request, id, rating): # DONE
    context = {}
    user_info = get_object_or_404(UserInfo, user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    rated_user = get_object_or_404(User,id=id)
    rated_user_info = get_object_or_404(UserInfo,user=rated_user)
    #rated_user_info = UserInfo.objects.get(user=rated_user)
    
    if int(rating) > 5 or int(rating) < 0: # avoid spoofed input
        # do nothing
        context['user_info'] = user_info
        context['viewed_user_info'] = viewed_user_info
        context['user_comments'] = user_comments
        context['form'] = CommentForm()
        return redirect('/potluck/profile/' + str(rated_user_info.user.id), context)
        
    rated_user_info.num_ratings += 1
    rated_user_info.total_rating += float(rating)
    rated_user_info.average_rating = rated_user_info.total_rating/rated_user_info.num_ratings
    rated_user_info.save()
    
    # return profile of subject user
    viewed_user_info = UserInfo.objects.get(user__id=id)
    user_comments = UserComment.objects.filter(subject=viewed_user_info.user)
    context['user_info'] = user_info
    context['viewed_user_info'] = viewed_user_info
    context['user_comments'] = user_comments
    context['form'] = CommentForm()
    return redirect('/potluck/profile/' + str(rated_user_info.user.id), context)

def comment_on_user(request, id): # DONE
    context = {}
    user_info = get_object_or_404(UserInfo, user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    subject_user = get_object_or_404(User, id=id)
    #subject_user = User.objects.get(id=id)
    subject_user_info = get_object_or_404(UserInfo, user=subject_user)
    #subject_user_info = UserInfo.objects.get(user=subject_user)
    form = CommentForm(request.POST)
    if not form.is_valid():
      print "comment_on_user: invalid form", form.errors
      context['form'] = form
      return render(request, 'profile.html', context)
    text = form.cleaned_data['text']
    comment = UserComment(subject=subject_user, author=request.user,text=text)
    comment.save()
    # return profile of subject user
    viewed_user_info = UserInfo.objects.get(user__id=id)
    user_comments = UserComment.objects.filter(subject=viewed_user_info.user)
    context['user_info'] = user_info
    context['viewed_user_info'] = viewed_user_info
    context['user_comments'] = user_comments
    context['form'] = CommentForm()
    return render(request, 'profile.html', context)

@login_required
def sell(request): # DONE?
    # What happens if you try to submit without a picture?
    context = {}
    user_info = get_object_or_404(UserInfo, user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    context['user_info'] = user_info
    
    if request.method == 'GET':
      print "sell: GET"
      context['form'] = SellForm()
      return render(request, 'sell.html', context)
    
    print "sell: POST"
    form = SellForm(request.POST, request.FILES)
    if (not form.is_valid()) or (not ('picture' in request.FILES)):
      print "sell: invalid form", form.errors
      context['form'] = form
      return render(request, 'sell.html', context)
    print "sell: creating new item..."
    new_sale_item = SaleItem(seller=user_info,name=form.cleaned_data['name'],brand=form.cleaned_data['brand'],quantity=form.cleaned_data['quantity'],
      description=form.cleaned_data['description'],price=form.cleaned_data['price'],purchase_date=form.cleaned_data['purchase_date'],
      expiration_date=form.cleaned_data['expiration_date'],picture=request.FILES['picture'])
    new_sale_item.save()
    print "sell: new item saved"
    # form = SellForm(request.POST)
    # if not form.is_valid():
      # # TODO: go back to original page
      # return render(request, 'index.html', context)
    # user_info = UserInfo.objects.get(user=request.user)
    # new_sale_item = SaleItem(ingredient=form.cleaned_data['ingredient_name'], price = form.cleaned_data['price'], seller=user_info, expiration_date = form.cleaned_data['expiration_date'])
    # new_sale_item.save()
    # context['item'] = new_sale_item
    return redirect('/potluck/buy/', context)
    
@login_required
def selling(request): # DONE
    context = {}
    user_info = get_object_or_404(UserInfo, user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    items = SaleItem.objects.filter(seller=user_info)
    context['user_info'] = user_info
    context['items'] = items
    # form = SellForm(request.POST)
    # if not form.is_valid():
      # # TODO: go back to original page
      # return render(request, 'index.html', context)
    # user_info = UserInfo.objects.get(user=request.user)
    # new_sale_item = SaleItem(ingredient=form.cleaned_data['ingredient_name'], price = form.cleaned_data['price'], seller=user_info, expiration_date = form.cleaned_data['expiration_date'])
    # new_sale_item.save()
    # context['item'] = new_sale_item
    return render(request, 'selling.html', context)

@login_required
def profile(request, id): # DONE
    context = {}
    user_info = get_object_or_404(UserInfo, user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    viewed_user_info = UserInfo.objects.get(user__id=id)
    user_comments = UserComment.objects.filter(subject=viewed_user_info.user)
    user_items = SaleItem.objects.filter(seller=user_info)
    context['user_info'] = user_info
    context['viewed_user_info'] = viewed_user_info
    context['user_comments'] = user_comments
    context['form'] = CommentForm()
    context['items'] = user_items
    return render(request, 'profile.html', context)

def slash_price(request, id, amt): # DONE
    context = {}
    user_info = get_object_or_404(UserInfo, user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    item = SaleItem.objects.get(id=id)
    amt = int(amt)
    newProportion = (100.0-amt)/100.0
    item.price = round(float(item.price)*newProportion, 2)
    item.save()
    return redirect('/potluck/selling/', context)

def category(request, term):
    context = {}
    user_info = get_object_or_404(UserInfo, user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    context['user_info'] = user_info
    
    keywords = []
    if term == 'vegetables':
        keywords = ['lettuce','tomato','eggplant','cabbage','pepper','onion','broccoli','bean',
            'celery','beet','corn','spinach','bok choy','pea','carrot','sprout','avocado',
            'cucumber','zucchini','pumpkin','melon','vegetable','potato']
    elif term == 'fruits':
        keywords = ['apple','orange','banana','berry','kiwi','pear','grape','fruit',
            'plum','persimmon','mango','coconut','cherry','lemon','lime','lychee','olive','peach',
            'pomegranate','raisin','tangerine','apricot']
    elif term == 'packaged':
        keywords = ['chips','package','bar','frozen','premade']
    elif term == 'drinks':
        keywords = ['water','soda','cola','seltzer','sprite','coke','pepsi','dr. pepper',
            'mountain dew','juice','tea','coffee','milk','drink','cider']
    elif term == 'snacks':
        keywords = ['chips','salsa','bar','snack','cookie','cake','brownie','dip','ice cream',
            'guacamole','straw','popcorn','biscuit','cracker','pretzel','nut','yogurt','jerky']
    elif term == 'healthy':
        keywords = ['acai','superfood','healthy','low-fat']
        keywords += ['lettuce','tomato','eggplant','cabbage','pepper','onion','broccoli','bean',
            'celery','beet','corn','spinach','bok choy','pea','carrot','sprout','avocado',
            'cucumber','zucchini','pumpkin','melon','vegetable','potato'] # add keywords from vegetables
        keywords += ['apple','orange','banana','berry','kiwi','pear','grape','fruit',
            'plum','persimmon','mango','coconut','cherry','lemon','lime','lychee','olive','peach',
            'pomegranate','raisin','tangerine','apricot'] # add keywords from fruit
    # otherwise, no keywords
    
    search_results = SaleItem.objects.none()
    print term, keywords
    for keyword in keywords:
        partial_name_results = SaleItem.objects.filter(name__icontains=keyword)
        partial_desc_results = SaleItem.objects.filter(description__icontains=keyword)
        search_results = search_results | partial_name_results | partial_desc_results
    
    context['items'] = get_rows(search_results)
    return render(request, 'buy.html', context)
    
@login_required
def my_account(request): # DONE
    context = {}
    user_info = get_object_or_404(UserInfo, user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    context['user_info'] = user_info
    user_items = SaleItem.objects.filter(seller=user_info)
    context['items'] = user_items
    
    if request.method == 'GET':
        context['form'] = UserProfileInfoForm()
        return render(request, 'my-account.html', context)
    
    # POST - edit profile fields
    # Check the validity of the form data
    form = UserProfileInfoForm(request.POST, request.FILES)
    context['form'] = form
    if not form.is_valid():
        print form.errors
        return render(request, 'my-account.html', context)
    
    if 'avatar' in request.FILES:
        user_info.avatar = request.FILES['avatar']
    
    print "editprofile - editing"
    # edit profile information
    #user_info.name = form.cleaned_data['name']
    user_info.phone = form.cleaned_data['phone']
    
    user_info.show_email = form.cleaned_data['show_email']
    
    user_info.save()
    
    #return render(request, 'my-account.html', context)
    return redirect('/potluck/profile/' + str(user_info.user.id), context)

def change_password(request):
    context = {}
    user_info = get_object_or_404(UserInfo, user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    context['user_info'] = user_info
    
    if request.method == 'GET':
      context['form'] = ChangePasswordForm()
      return render(request, 'my-account.html', context)
    # POST
    form = ChangePasswordForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        print form.errors
        return render(request, 'my-account.html', context)
    current_password = form.cleaned_data['current_password']
    new_password_1 = form.cleaned_data['new_password_1']
    # no need to check most of the logic since we did that in validation, but we do need to check whether the fields have been filled in to begin with
    if current_password and new_password_1:
      user = authenticate(username=user_info.user.username, password=current_password)
      if user is not None:
        request.user.set_password(form.cleaned_data['new_password_1'])
        request.user.save()
      else:
        errors = []
        errors.append('Password was entered incorrectly.')
        context['errors'] = errors
    user_info.save()
    
    #return render(request, 'my-account.html', context)
    return redirect('/potluck/profile/' + str(user_info.user.id), context)

    
@login_required
def search(request):
    context = {}
    user_info = get_object_or_404(UserInfo, user=request.user)
    #user_info = UserInfo.objects.get(user=request.user)
    context['user_info'] = user_info
    
    #if request.method == 'GET':
    #    context['form'] = SearchForm()
    #    return render(request, 'search.html', context)
    
    # POST
    form = SearchForm(request.POST)
    if not form.is_valid():
        context['errors'] = form.errors
        return render(request, 'buy.html', context)
    search_term = form.cleaned_data['search_term']
    search_results = SaleItem.objects.none()
    if ' ' in search_term:
        print "multiple", search_term
        parts = search_term.split(' ')
        for part in parts:
            partial_name_results = SaleItem.objects.filter(name__icontains=part)
            partial_desc_results = SaleItem.objects.filter(description__icontains=part)
            search_results = search_results | partial_name_results | partial_desc_results
        print search_results
    else:
        print "single", search_term
        name_results = SaleItem.objects.filter(name__icontains=search_term)
        desc_results = SaleItem.objects.filter(description__icontains=search_term)
        search_results = name_results | desc_results
        print search_results
    context['search_term'] = search_term
    context['items'] = context['items'] = get_rows(search_results)
    return render(request, 'buy.html', context)
    
    
    
    context['form'] = form
    if not form.is_valid():
        return render(request, 'search.html', context)
    else:
      search_term = form.cleaned_data['search_term']
      matching_grumbls = Grumbl.objects.filter(grumbl__contains=search_term).exclude(user__in=user_info.blocked.all())
      context['matching_grumbls'] = matching_grumbls
      return render(request, 'search.html', context)

@login_required
def get_avatar(request, id):
  user = get_object_or_404(UserInfo, id=id)
  user_info = get_object_or_404(UserInfo, user=user)
  content_type = guess_type(user_info.avatar.name)
  try:
    response = HttpResponse(user_info.avatar, content_type=content_type)
    return response
  except Exception as e:
    print e

@login_required
def get_picture(request, id):
    item = get_object_or_404(SaleItem, id=id)
    if not item.picture:
        raise Http404
    content_type = guess_type(item.picture.name)
    return HttpResponse(item.picture, content_type = content_type)

# @login_required
# def offer(request):
    # context = {}
    # user_info = UserInfo.objects.get(user=request.user)
    # context['user'] = request.user
    # return render(request, 'index.html', context)

# @login_required
# def view_map(request):
    # context = {}
    # user_info = UserInfo.objects.get(user=request.user)
    # context['user'] = request.user
    # return render(request, 'index.html', context)
    

    

    
def forgotpassword(request):
        return render(request,'reset-password.html',{})

def resetpassword(request):
    context = {}
    if request.method == 'GET':
        context['form'] = ResetForm()
        return render(request, 'reset-password.html', context)

    form = ResetForm(request.POST)
    context['form'] = form
    if not form.is_valid():
            return render(request, 'reset-password.html',context)
    username = form.cleaned_data['username']
    email = form.cleaned_data['email']
    user = User.objects.get(username__exact=username,email__exact=email)
    if user:
        # reset password
        token = default_token_generator.make_token(user)
        email_body = "Click the link below to verify your e-mail address to reset your Potluck password: http://%s%s" % (request.get_host(),  reverse('reset-confirm', args=(username, token)))
        send_mail(subject="[Potluck] Reset your password",
                message= email_body,
                from_email="syyang@andrew.cmu.edu",
                recipient_list=[email])
        context['email'] = email
        return render(request, 'reset-password-done.html', context)
    else:
       errors = []
       errors.append("No user found with the specified information.")
       context['errors'] = errors
       return render(request, 'reset-password.html',context)

def resetpassword_confirm(request, username, token):
    context={}
    context['username'] = username
    if request.method == 'GET':
        user = get_object_or_404(User, username=username)
        # Send 404 error if token is invalid
        if not default_token_generator.check_token(user, token):
            raise Http404
        else:
            context['username'] = username
            return render(request,'reset-password-confirm.html',context)

def resetpassword_check(request, username):
    print "resetpassword_check"
    context={}
    if not request.method == 'POST':
        return
    # POST
    user = get_object_or_404(User, username=username)
    form = ResetPasswordForm(request.POST)
    if not form.is_valid():
        errors = []
        errors.add("Passwords must match.")
        context['errors'] = errors
        return render(request,'reset-password-confirm.html',context)
    pass1 = form.cleaned_data['password1']
    pass2 = form.cleaned_data['password2']
    if (pass1 == pass2): # necessary?
        user.set_password(pass1)
        user.save()
        print "resetpassword_check: password set correctly for",user.username,":",pass1
        return render(request, 'reset-password-complete.html',context)
    else:
        return render(request,'reset-password-confirm.html',context)
        
      
@transaction.atomic    
def register(request):
    print "views.py: register"
    context = {}

    # Just display the registration form if this is a GET request
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'register.html', context)

    # POST
    # Check the validity of the form data
    
    print "views.py: register 1"
    
    form = RegistrationForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        print "invalid registration form"
        print form.errors
        return render(request, 'register.html', context)
    
    print "views.py: register 2"
    
    if not 'username' in request.POST or not request.POST['username']:
      errors.append('Username is required.')
    else:
        # Save the username in the request context to re-fill the username
        # field in case the form has errrors
      context['username'] = request.POST['username']

    print "views.py: register 3"
    
    # Creates the new user from the valid form data
    context['errors'] = form.errors
    if form.cleaned_data['phone']:
        new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        email=form.cleaned_data['email'],
                                        phone=form.cleaned_data['phone'])
    else:
        new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        email=form.cleaned_data['email'],
                                        password=form.cleaned_data['password1'])
    print "views.py: register 4"
    
    new_user.is_active = False;
    new_user.save()
    
    new_userinfo = UserInfo(user=new_user)
    new_userinfo.save()
    
    

    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)

    email_body = "Welcome to Potluck! Click the link below to verify your e-mail address and complete your registration: http://%s%s" % (request.get_host(),  reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="[Potluck] Verify your email address",
              message= email_body,
              from_email="syyang@andrew.cmu.edu",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']
    return render(request, 'needs-verification.html', context)
    # Logs in the new user and redirects to his/her todo list
    #new_user = authenticate(username=form.cleaned_data['username'], \
    #                        password=form.cleaned_data['password1'])
    #login(request, new_user)


@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    return render(request, 'email-verified.html', {})