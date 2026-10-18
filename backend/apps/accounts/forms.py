from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.text import slugify


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        label="Full name",
        widget=forms.TextInput(attrs={"autocomplete": "name", "class": "input"}),
    )
    username = forms.CharField(required=False, widget=forms.HiddenInput())
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(("full_name", "email", "username", "password1", "password2"))
        for field in self.fields.values():
            if not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs.setdefault("class", "input")

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("username"):
            email = cleaned_data.get("email", "")
            base_username = slugify(email.split("@", 1)[0])[:140] or "customer"
            username = base_username
            suffix = 2
            while User.objects.filter(username=username).exists():
                username = f"{base_username[:140-len(str(suffix))]}-{suffix}"
                suffix += 1
            cleaned_data["username"] = username
        if not cleaned_data.get("full_name"):
            cleaned_data["full_name"] = cleaned_data.get("username", "")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        name_parts = self.cleaned_data.get("full_name", "").strip().split(maxsplit=1)
        user.first_name = name_parts[0] if name_parts else ""
        user.last_name = name_parts[1] if len(name_parts) > 1 else ""
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={"class": "input", "autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "input", "autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": "Please enter a correct email address and password.",
        "inactive": "This account is inactive.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def get_user(self):
        return self.user_cache

    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            return False
        from django.contrib.auth import authenticate

        email = self.cleaned_data["email"].strip()
        user = User.objects.filter(email__iexact=email).first()
        self.user_cache = authenticate(
            self.request,
            username=user.get_username() if user else email,
            password=self.cleaned_data["password"],
        )
        if self.user_cache is None:
            self.add_error(None, self.error_messages["invalid_login"])
            return False
        return True


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "input", "autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"class": "input", "autocomplete": "family-name"}),
            "email": forms.EmailInput(attrs={"class": "input", "autocomplete": "email"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
