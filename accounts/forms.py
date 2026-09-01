from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from .models import Profile




class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class LoginForm(AuthenticationForm):

    error_messages = {
        "invalid_login":
            "Password not match. Please try again.",

        "inactive":
            "This account is inactive.",
    }

    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "autocomplete": "username",
            }
        ),
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        ),
    )

class ForgotPasswordForm(forms.Form):
    account = forms.CharField(
        label="Username or Email",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter username or email",
                "autocomplete": "username",
            }
        ),
    )

class PasswordResetForm(forms.Form):

    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter new password",
                "autocomplete": "new-password",
            }
        ),
        validators=[validate_password],
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm new password",
                "autocomplete": "new-password",
            }
        ),
    )

    def clean(self):

        cleaned_data = super().clean()

        new_password = cleaned_data.get(
            "new_password"
        )

        confirm_password = cleaned_data.get(
            "confirm_password"
        )

        if (
            new_password
            and confirm_password
            and new_password != confirm_password
        ):

            raise forms.ValidationError(
                "New Password and Confirm Password do not match."
            )

        return cleaned_data

    # =========================================================
# EDIT PROFILE FORM
# =========================================================

class EditProfileForm(forms.ModelForm):

    email = forms.EmailField(
        required=True
    )


    class Meta:

        model = User

        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
        ]


        widgets = {

            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "First name",
                    "autocomplete": "given-name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Last name",
                    "autocomplete": "family-name",
                }
            ),

            "username": forms.TextInput(
                attrs={
                    "placeholder": "Username",
                    "autocomplete": "username",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email address",
                    "autocomplete": "email",
                }
            ),
        }

        
        
# =========================================================
# PROFILE PICTURE FORM
# =========================================================

class ProfilePictureForm(forms.ModelForm):

    class Meta:

        model =  Profile

        fields = [
            "profile_picture",
        ]

        widgets = {

            "profile_picture": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*",
                }
            ),
        }



        
# =========================================================
# CHANGE PASSWORD FORM
# =========================================================

class ChangePasswordForm(forms.Form):

    current_password = forms.CharField(
        label="Current Password",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter current password",
                "autocomplete": "current-password",
            }
        ),
    )


    new_password = forms.CharField(
        label="New Password",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter new password",
                "autocomplete": "new-password",
            }
        ),
        validators=[
            validate_password,
        ],
    )


    confirm_password = forms.CharField(
        label="Confirm New Password",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm new password",
                "autocomplete": "new-password",
            }
        ),
    )


    def clean(self):

        cleaned_data = super().clean()

        new_password = cleaned_data.get(
            "new_password"
        )

        confirm_password = cleaned_data.get(
            "confirm_password"
        )


        # =================================================
        # PASSWORD MATCH
        # =================================================

        if (
            new_password
            and confirm_password
            and new_password != confirm_password
        ):

            raise forms.ValidationError(
                "New Password and Confirm Password do not match."
            )


        return cleaned_data

# =========================================================
# PRIVACY FORM
# =========================================================

class PrivacyForm(forms.Form):

    profile_visibility = forms.ChoiceField(
        label="Profile Visibility",
        choices=[
            (
                "everyone",
                "Everyone"
            ),
            (
                "followers",
                "People you follow"
            ),
            (
                "private",
                "Only me"
            ),
        ],
        widget=forms.RadioSelect,
    )


    message_privacy = forms.ChoiceField(
        label="Who can message you?",
        choices=[
            (
                "everyone",
                "Everyone"
            ),
            (
                "followers",
                "People you follow"
            ),
            (
                "no_one",
                "No one"
            ),
        ],
        widget=forms.RadioSelect,
    )


       
# =========================================================
# NOTIFICATION FORM
# =========================================================

class NotificationForm(forms.Form):

    email_notifications = forms.BooleanField(
        required=False,
        label="Email Notifications",
    )

    login_alerts = forms.BooleanField(
        required=False,
        label="Login Alerts",
    )

    meeting_notifications = forms.BooleanField(
        required=False,
        label="Meeting Notifications",
    )

    account_activity_notifications = forms.BooleanField(
        required=False,
        label="Account Activity",
    )     