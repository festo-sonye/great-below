from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, SellerProfile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))
    phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))
    user_type = forms.ChoiceField(choices=[('customer', 'Customer'), ('seller', 'Seller')], widget=forms.RadioSelect(attrs={
        'class': 'form-check-input'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'user_type', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomUserLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email',
        'autofocus': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'


class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ('shop_name', 'shop_description', 'shop_image', 'phone_number', 'shop_address', 'bank_name', 'bank_account', 'mpesa_number')
        widgets = {
            'shop_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Shop Name'
            }),
            'shop_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your shop...',
                'rows': 4
            }),
            'shop_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'shop_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Shop Address',
                'rows': 3
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank Name'
            }),
            'bank_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank Account Number'
            }),
            'mpesa_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'M-PESA Number'
            }),
        }


class CustomUserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'profile_image')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
