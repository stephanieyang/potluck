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

@login_required
def home(request):
    context = {}
    user_info = UserInfo.objects.get(user=request.user)
    context['user_info'] = user_info
    return render(request, 'index.html', context)
    
@login_required
def buy(request):
    context = {}
    items = SaleItem.objects.none() # TODO: implement this
    user_info = UserInfo.objects.get(user=request.user)
    context['user_info'] = user_info
    context['items'] = items
    return render(request, 'buy.html', context)

@login_required
def edit_sale(request, id):
    context = {}
    user_info = UserInfo.objects.get(user=request.user)
    item = SaleItem.objects.get(id=id) # TODO: implement this better?
    context['user_info'] = user_info
    context['item'] = item
    return render(request, 'edit-sale.html', context)

@login_required
def sell(request):
    context = {}
    user_info = UserInfo.objects.get(user=request.user)
    context['user_info'] = user_info
    # form = SellForm(request.POST)
    # if not form.is_valid():
      # # TODO: go back to original page
      # return render(request, 'index.html', context)
    # user_info = UserInfo.objects.get(user=request.user)
    # new_sale_item = SaleItem(ingredient=form.cleaned_data['ingredient_name'], price = form.cleaned_data['price'], seller=user_info, expiration_date = form.cleaned_data['expiration_date'])
    # new_sale_item.save()
    # context['item'] = new_sale_item
    return render(request, 'sell.html', context)
    
@login_required
def selling(request):
    context = {}
    user_info = UserInfo.objects.get(user=request.user)
    items = SaleItem.objects.none() # TODO: implement this
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
def profile(request, id):
    context = {}
    user_info = UserInfo.objects.get(user=request.user)
    viewed_user_info = UserInfo.objects.get(user__id=id)
    user_comments = UserComment.objects.filter(subject=viewed_user_info.user)
    context['user_info'] = user_info
    context['viewed_user_info'] = viewed_user_info
    context['user_comments'] = user_comments
    return render(request, 'profile.html', context)

def slash_price(request, id, amt):
    context = {}
    user_info = UserInfo.objects.get(user=request.user)
    # TODO: implement price slash
    return render(request, 'selling.html', context)
    
@login_required
def edit_profile(request):
    context = {}
    user_info = UserInfo.objects.get(user=request.user)
    viewed_user_info = UserInfo.objects.get(user__id=id)
    context['user_info'] = user_info
    return render(request, 'edit-profile.html', context)
    
@login_required
def search(request):
    context = {}
    user_info = UserInfo.objects.get(user=request.user)
    search_results = SaleItem.objects.none() # TODO: implement this better
    context['user_info'] = user_info
    context['search_results'] = search_results
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
    if not item.image:
        raise Http404
    content_type = guess_type(item.image.name)
    return HttpResponse(item.image, content_type = content_type)

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
    form = RegistrationForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        print "invalid registration form"
        print form.errors
        return render(request, 'register.html', context)
    
    if not 'username' in request.POST or not request.POST['username']:
      errors.append('Username is required.')
    else:
        # Save the username in the request context to re-fill the username
        # field in case the form has errrors
      context['username'] = request.POST['username']

    # Creates the new user from the valid form data
    context['errors'] = form.errors
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        email=form.cleaned_data['email'],
                                        password=form.cleaned_data['password1'])
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