from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True
    )

    bio = models.TextField(
        max_length=500,
        blank=True
    )


    # =====================================================
    # PRIVACY SETTINGS
    # =====================================================

    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ("everyone", "Everyone"),
            ("followers", "People you follow"),
            ("private", "Only me"),
        ],
        default="everyone",
    )

    message_privacy = models.CharField(
        max_length=20,
        choices=[
            ("everyone", "Everyone"),
            ("followers", "People you follow"),
            ("no_one", "No one"),
        ],
        default="everyone",
    )


    # =====================================================
    # NOTIFICATION SETTINGS
    # =====================================================

    email_notifications = models.BooleanField(
        default=True
    )

    login_alerts = models.BooleanField(
        default=True
    )

    meeting_notifications = models.BooleanField(
        default=True
    )

    account_activity_notifications = models.BooleanField(
        default=True
    )


    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __str__(self):

        return self.user.username