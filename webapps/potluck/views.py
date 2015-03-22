ffrom django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.db import transaction

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from potluck.models import *
import time, datetime

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
    context['user'] = request.user
    return render(request, 'index.html', context)
    
@login_required
def buy(request, ingredient_name):
    matching_ingredients = Ingredient.objects.filter(name__icontains=ingredient_name)
    context = {}
    user_info = UserInfo.objects.get(user=request.user)
    context['user'] = request.user
    context['matches'] = matching_ingredients
    return render(request, 'index.html', context)

@login_required
def sell(request):
    context = {}
    user_info = UserInfo.objects.get(user=request.user)
    form = SellForm(request.POST)
    if not form.is_valid():
      # TODO: go back to original page
      return render(request, 'index.html', context)
    user_info = UserInfo.objects.get(user=request.user)
    new_sale_item = SaleItem(ingredient=form.cleaned_data['ingredient_name'], price = form.cleaned_data['price'], seller=user_info, expiration_date = form.cleaned_data['expiration_date'])
    new_sale_item.save()
    context['item'] = new_sale_item
    return render(request, 'index.html', context)

@login_required
def offer(request):
    context = {}
    user_info = UserInfo.objects.get(user=request.user)
    context['user'] = request.user
    return render(request, 'index.html', context)

@login_required
def view_map(request):
    context = {}
    user_info = UserInfo.objects.get(user=request.user)
    context['user'] = request.user
    return render(request, 'index.html', context)