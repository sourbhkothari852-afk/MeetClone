from django.db import models
from django.contrib.auth.models import User


class Meeting(models.Model):

    # =====================================================
    # HOST
    # =====================================================

    host = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="hosted_meetings"
    )


    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )


    # =====================================================
    # MEETING CODE
    # =====================================================

    meeting_code = models.CharField(
        max_length=20,
        unique=True
    )


    # =====================================================
    # SCHEDULE
    # =====================================================

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True
    )


    # =====================================================
    # STATUS
    # =====================================================

    STATUS_CHOICES = [

        ("scheduled", "Scheduled"),

        ("live", "Live"),

        ("completed", "Completed"),

        ("cancelled", "Cancelled"),

    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="scheduled"
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

        return self.title



# =====================================================
# MEETING PARTICIPANT
# =====================================================

class MeetingParticipant(models.Model):

    # =================================================
    # MEETING
    # =================================================

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="participants"
    )


    # =================================================
    # USER
    # =================================================

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="joined_meetings"
    )


    # =================================================
    # JOIN TIME
    # =================================================

    joined_at = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "meeting",
                    "user",
                ],
                name="unique_meeting_participant"
            )

        ]


    def __str__(self):

        return (
            f"{self.user.username} "
            f"joined {self.meeting.title}"
        )