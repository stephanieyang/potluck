from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from models import *

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
    phone = forms.CharField(max_length=12, required=False)
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

        # Check the passwords
        current_password = cleaned_data.get('current_password')
        new_password_1 = cleaned_data.get('new_password_1')
        new_password_2 = cleaned_data.get('new_password_2')
        # both if new password fields have been filled in...
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