from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from notifications.models import Notification
from meetings.models import (
    Meeting,
    MeetingParticipant,
)


@login_required
def home(request):

    # =====================================================
    # UNREAD NOTIFICATIONS
    # =====================================================

    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()


    # =====================================================
    # RECENT CREATED MEETINGS
    # =====================================================

    created_meetings = Meeting.objects.filter(
        host=request.user
    )


    # =====================================================
    # RECENT JOINED MEETINGS
    # =====================================================

    joined_meetings = MeetingParticipant.objects.filter(
        user=request.user
    ).select_related(
        "meeting",
        "meeting__host"
    )


    # =====================================================
    # RENDER HOME PAGE
    # =====================================================

    return render(
        request,
        "home.html",
        {
            "unread_count": unread_count,
            "created_meetings": created_meetings,
            "joined_meetings": joined_meetings,
        }
    )