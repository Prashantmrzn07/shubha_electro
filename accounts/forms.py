import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm

User = get_user_model()


class StyledFormMixin:
    def _style_fields(self):
        for field in self.fields.values():
            field.help_text = ""
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css} input".strip()


class RegisterForm(StyledFormMixin, forms.ModelForm):
    """
    YouTube/Google-style registration form:
    - Does NOT ask for a separate username (Gmail is the account identity)
    - Validates strictly for valid @gmail.com accounts
    - Removes cluttered Django default help texts from placeholders
    """
    first_name = forms.CharField(
        max_length=60,
        required=True,
        label="First name",
        widget=forms.TextInput(attrs={"placeholder": "First name", "autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        max_length=60,
        required=True,
        label="Last name",
        widget=forms.TextInput(attrs={"placeholder": "Last name", "autocomplete": "family-name"}),
    )
    email = forms.EmailField(
        required=True,
        label="Gmail address",
        widget=forms.EmailInput(
            attrs={"placeholder": "example@gmail.com", "autocomplete": "email", "type": "email"}
        ),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "autocomplete": "new-password"}
        ),
        strip=False,
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm password", "autocomplete": "new-password"}
        ),
        strip=False,
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label="Phone number (optional)",
        widget=forms.TextInput(attrs={"placeholder": "Phone number (optional)", "autocomplete": "tel"}),
    )
    address = forms.CharField(
        required=False,
        label="Delivery address (optional)",
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Delivery address (optional)"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "address"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError("Gmail address is required.")

        # Require a valid @gmail.com address
        gmail_pattern = r"^[a-zA-Z0-9._%+-]+@gmail\.com$"
        if not re.match(gmail_pattern, email):
            raise forms.ValidationError("Please provide a valid Gmail address ending in @gmail.com.")

        # Ensure account is unique across both email and username
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("An account with this Gmail address already exists.")

        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2:
            if p1 != p2:
                self.add_error("password2", "The passwords do not match.")
            elif len(p1) < 8:
                self.add_error("password1", "Password must be at least 8 characters long.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].strip().lower()
        user.username = email
        user.email = email
        user.role = User.ROLE_CUSTOMER
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(StyledFormMixin, AuthenticationForm):
    username = forms.CharField(
        label="Gmail or Username",
        widget=forms.TextInput(
            attrs={"placeholder": "Gmail address or username", "autofocus": True, "autocomplete": "username"}
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "autocomplete": "current-password"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class AdminLoginForm(LoginForm):
    username = forms.CharField(
        label="Admin Gmail or Username",
        widget=forms.TextInput(
            attrs={
                "placeholder": "prashantmhrh77@gail.com or admin",
                "autofocus": True,
                "autocomplete": "username",
            }
        ),
    )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not getattr(user, "is_shop_admin", False):
            raise forms.ValidationError(
                "This login is for administrators only.",
                code="admin_login_required",
            )


class ProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "address"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Gmail address"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone number"}),
            "address": forms.Textarea(attrs={"rows": 3, "placeholder": "Delivery address"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class AdminUserForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "role",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ""
            field.widget.attrs["class"] = "input"
