from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from auto.models import UserWithoutAccount, Order


class SignUpForm(UserCreationForm):
    full_Name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(max_length=254, required=True)
    address = forms.CharField(max_length=30, required=True,)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        for fieldname in ['password1', 'password2']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = get_user_model()
        fields = ('full_Name', 'email', 'password1', 'password2', 'address')


class SignInForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)


class UserOrderForm(forms.ModelForm):
    class Meta:
        model = UserWithoutAccount
        fields = ['first_name', 'last_name','email','contact_number','address']


class SimpleOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'item_id', 'item_name', 'item_price', 'payment_status', 'charge_id']