from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from models import *


        
class SellForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        exclude = ('seller','posted_time','picture')
        
    def clean(self):
        cleaned_data = super(SellForm, self).clean()
        if len(str(cleaned_data.get('price')).split('.')[1]) > 2: # more than two decimal places
            raise forms.ValidationError("Please enter a valid price.")
        if len(str(cleaned_data.get('price')).split('.')[0]) > 3: # more than $999
            raise forms.ValidationError("Please enter a price from $0.00-$999.99.")
        return cleaned_data
        
class EditSaleForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        exclude = ('seller','name','posted_time','picture')
        
    def clean(self):
        cleaned_data = super(EditSaleForm, self).clean()
        if len(str(cleaned_data.get('price')).split('.')[1]) > 2: # more than two decimal places
            raise forms.ValidationError("Please enter a valid price.")
        if len(str(cleaned_data.get('price')).split('.')[0]) > 3: # more than $999
            raise forms.ValidationError("Please enter a price from $0.00-$999.99.")
        return cleaned_data

class SearchForm(forms.Form):
    search_term = forms.CharField(max_length=255)
        
    def clean(self):
        print "SearchForm clean"
        cleaned_data = super(SearchForm, self).clean()
        search_term = cleaned_data.get('search_term')
        if cleaned_data.get('search_term'):
            search_term = cleaned_data.get('search_term')
            if search_term != None:
                if len(search_term) > 0:
                    print "SearchForm: got search_term", search_term
                else:
                    print "2"
                    raise forms.ValidationError("Please enter a term to search.")
            else:
                print "3"
                raise forms.ValidationError("Please enter a term to search.")
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = UserComment
        exclude = ('subject','author','time')
        
    def clean(self):
        cleaned_data = super(CommentForm, self).clean()
        if len(cleaned_data.get('text')) == 0: # more than two decimal places
            raise forms.ValidationError("Please enter a nonempty comment.")
        return cleaned_data
        
class RegistrationForm(forms.Form):
    username = forms.CharField(max_length = 20)
    email = forms.CharField(max_length = 50)
    password1 = forms.CharField(max_length = 200, 
                                label='Password', 
                                widget = forms.PasswordInput())
    password2 = forms.CharField(max_length = 200, 
                                label='Confirm password',  
                                widget = forms.PasswordInput())
    phone = forms.CharField(max_length = 12,required=False)


    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        print "RegistrationForm clean"
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()
        print(cleaned_data)

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")
        phone = cleaned_data.get('phone')
        if phone == None or len(phone) == 0:
          pass # this is okay

        return cleaned_data


    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # Generally return the cleaned data we got from the cleaned_data
        # dictionary
        return username

    
class UserProfileInfoForm(forms.Form):
    # don't use ModelForms, in order to store things like username, name, etc. in User
    class Meta:
        widgets = {'avatar':forms.FileInput()}
    
    avatar = forms.FileField(required=False);
    phone = forms.CharField(min_length=10,max_length=15, required=False)
    show_email = forms.BooleanField(required=False)
    current_password = forms.CharField(max_length = 200,  
                                widget = forms.PasswordInput(), required=False)
    new_password_1 = forms.CharField(max_length = 200, 
                                widget = forms.PasswordInput(), required=False)
    new_password_2 = forms.CharField(max_length = 200, 
                                widget = forms.PasswordInput(), required=False)  
    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(UserProfileInfoForm, self).clean()
        
        # check that at least one of phone and e-mail will display
        phone = cleaned_data.get('phone')
        show_email = cleaned_data.get('show_email')
        if (len(phone) == 0) and (not show_email):
            raise forms.ValidationError("At least one of phone number and email must be displayed.")

        # Check the passwords
        current_password = cleaned_data.get('current_password')
        new_password_1 = cleaned_data.get('new_password_1')
        new_password_2 = cleaned_data.get('new_password_2')
        # if both new password fields have been filled in...
        if new_password_1 and new_password_2:
          # check that they're the same
          if new_password_1 != new_password_2:
            raise forms.ValidationError("Passwords did not match.")
          # and that the user has entered the correct current password
          if not current_password:
            raise forms.ValidationError("Must provide current password.")
          # can this be done here? requires information about the user, which required request.user in views.py
          else:
            if self.instance:
              user = authenticate(username=self.instance.username, password=current_password)
              if user is None:
                raise forms.ValidationError("Current password entered incorrectly.")
            else:
              raise forms.ValidationError("Form error: could not get current user instance.")

        # Generally return the cleaned data we got from our parent.
        return cleaned_data



class ResetForm(forms.Form):
    username = forms.CharField(max_length = 20)
    email = forms.CharField(max_length = 50)

    def clean(self):
        cleaned_data = super(ResetForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        if not User.objects.filter(username__exact=username,email__exact=email):
            raise forms.ValidationError("Incorrect username and email.")
        return cleaned_data

class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(max_length=200)
    password2 = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        pass1 = cleaned_data.get('password1')
        pass2 = cleaned_data.get('password2')
        if not (pass1 == pass2):
            raise forms.ValidationError("Passwords did not match")
        return cleaned_data