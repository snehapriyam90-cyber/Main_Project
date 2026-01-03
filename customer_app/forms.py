from django import forms
from django.contrib.auth.models import User
from .models import *


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}))

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('farmer', 'Farmer'),
    )
    username_or_email = forms.CharField(label="Username or Email")
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,  # Must select
        widget=forms.RadioSelect
    )

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'gender', 'age', 'phone']

class AddressForm(forms.ModelForm):
    state = forms.ChoiceField(choices=STATE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    district = forms.CharField(widget=forms.Select(attrs={'class': 'form-select'}))  # empty initially
    address_line = forms.CharField(widget=forms.Textarea(attrs={'rows':5}))


    class Meta:
        model = Address
        fields = ['address_line', 'state', 'district', 'pincode', 'is_default']

