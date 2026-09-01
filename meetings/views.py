from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.crypto import get_random_string

from .forms import (
    MeetingForm,
    JoinMeetingForm,
)

from .models import (
    Meeting,
    MeetingParticipant,
    )

# =====================================================
# NOTIFICATIONS
# =====================================================

from notifications.models import Notification


# =====================================================
# CREATE MEETING
# =====================================================

@login_required
def create_meeting_view(request):

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        form = MeetingForm(
            request.POST
        )

        # =================================================
        # VALIDATE FORM
        # =================================================

        if form.is_valid():

            meeting = form.save(
                commit=False
            )

            # =============================================
            # CURRENT USER = HOST
            # =============================================

            meeting.host = request.user

            # =============================================
            # GENERATE UNIQUE MEETING CODE
            # =============================================

            meeting.meeting_code = (
                get_random_string(
                    length=10
                ).upper()
            )

            # =============================================
            # DEFAULT STATUS
            # =============================================

            meeting.status = "scheduled"

            # =============================================
            # SAVE MEETING
            # =============================================

            meeting.save()

            # =============================================
            # CREATE AUTOMATIC NOTIFICATION
            # =============================================

            Notification.objects.create(
                recipient=request.user,
                notification_type="meeting",
                title="Meeting Created",
                message=(
                    f'Your meeting "{meeting.title}" '
                    f'has been created successfully. '
                    f'Meeting code: {meeting.meeting_code}'
                ),
            )

            # =============================================
            # GO TO MEETING DETAILS
            # =============================================

            return redirect(
                "meeting_detail",
                meeting_id=meeting.id
            )

    # =====================================================
    # GET
    # =====================================================

    else:

        form = MeetingForm()

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "meetings/create_meeting.html",
        {
            "form": form,
        },
    )


# =========================================================
# MEETING DETAIL
# =========================================================

@login_required
def meeting_detail_view(
    request,
    meeting_id
):

    meeting = get_object_or_404(
        Meeting,
        id=meeting_id
    )

    return render(
        request,
        "meetings/meeting_detail.html",
        {
            "meeting": meeting,
        },
    )

# =========================================================
# JOIN MEETING
# =========================================================

@login_required
def join_meeting_view(request):

    if request.method == "POST":

        form = JoinMeetingForm(
            request.POST
        )

        if form.is_valid():

            meeting_code = (
                form.cleaned_data["meeting_code"]
            )

            try:

                meeting = Meeting.objects.get(
                    meeting_code=meeting_code
                )

            except Meeting.DoesNotExist:

                form.add_error(
                    "meeting_code",
                    "Invalid meeting code. Meeting not found."
                )

            else:

                # =============================================
                # BLOCK COMPLETED MEETING
                # =============================================

                if meeting.status == "completed":

                    form.add_error(
                        "meeting_code",
                        "This meeting has ended."
                    )

                # =============================================
                # BLOCK CANCELLED MEETING
                # =============================================

                elif meeting.status == "cancelled":

                    form.add_error(
                        "meeting_code",
                        "This meeting has been cancelled."
                    )

                # =============================================
                # ALLOW ACTIVE MEETING
                # =============================================

                else:

                    # =============================================
                    # SAVE MEETING PARTICIPANT
                    # =============================================

                    MeetingParticipant.objects.get_or_create(
                        meeting=meeting,
                        user=request.user,
                    )

                    # =============================================
                    # CREATE JOIN MEETING NOTIFICATION
                    # =============================================

                    Notification.objects.create(
                        recipient=request.user,
                        notification_type="meeting",
                        title="Meeting Joined",
                        message=(
                            f'You joined the meeting "{meeting.title}". '
                            f'Meeting code: {meeting.meeting_code}'
                        ),
                    )

                    # =============================================
                    # OPEN MEETING ROOM
                    # =============================================

                    return redirect(
                        "meeting_room",
                        meeting_id=meeting.id
                    )

    else:

        form = JoinMeetingForm()

    # =====================================================
    # RENDER JOIN MEETING PAGE
    # =====================================================

    return render(
        request,
        "meetings/join_meeting.html",
        {
            "form": form,
        },
    )

# =========================================================
# MEETING ROOM
# =========================================================

@login_required
def meeting_room_view(
    request,
    meeting_id
):

    meeting = get_object_or_404(
        Meeting,
        id=meeting_id
    )

    return render(
        request,
        "meetings/meeting_room.html",
        {
            "meeting": meeting,
        },
    )




# =========================================================
# END MEETING
# =========================================================

@login_required
def end_meeting_view(
    request,
    meeting_id
):

    meeting = get_object_or_404(
        Meeting,
        id=meeting_id
    )

    # =====================================================
    # ONLY HOST CAN END THE MEETING
    # =====================================================

    if meeting.host != request.user:

        return redirect(
            "meeting_room",
            meeting_id=meeting.id
        )

    # =====================================================
    # END MEETING
    # =====================================================

    if request.method == "POST":

        # =====================================================
        # UPDATE STATUS ONLY IF NEEDED
        # =====================================================

        if meeting.status != "completed":

            meeting.status = "completed"

            meeting.save(
                update_fields=["status"]
            )

        # =====================================================
        # CREATE MEETING ENDED NOTIFICATION
        # =====================================================

        Notification.objects.create(
            recipient=request.user,
            notification_type="meeting",
            title="Meeting Ended",
            message=(
                f'Your meeting "{meeting.title}" '
                f'has ended successfully.'
            ),
        )

        return redirect("home")



    # =========================================================
# CANCEL MEETING
# =========================================================

@login_required
def cancel_meeting_view(request, meeting_id):

    meeting = get_object_or_404(
        Meeting,
        id=meeting_id
    )

    # =====================================================
    # ONLY HOST CAN CANCEL THE MEETING
    # =====================================================

    if meeting.host != request.user:

        return redirect(
            "meeting_detail",
            meeting_id=meeting.id
        )

    # =====================================================
    # CANCEL MEETING
    # =====================================================

    if request.method == "POST":

        if meeting.status != "cancelled":

            meeting.status = "cancelled"

            meeting.save(
                update_fields=["status"]
            )

        # =================================================
        # CREATE CANCELLED NOTIFICATION
        # =================================================

        Notification.objects.create(
            recipient=request.user,
            notification_type="meeting",
            title="Meeting Cancelled",
            message=(
                f'Your meeting "{meeting.title}" '
                f'has been cancelled.'
            ),
        )

        return redirect("home")

    return redirect(
        "meeting_detail",
        meeting_id=meeting.id
    )

# =========================================================
# LEAVE MEETING
# =========================================================

@login_required
def leave_meeting_view(request, meeting_id):

    meeting = get_object_or_404(
        Meeting,
        id=meeting_id
    )

    if request.method == "POST":

        Notification.objects.create(
            recipient=request.user,
            notification_type="meeting",
            title="Meeting Left",
            message=(
                f'You left the meeting "{meeting.title}".'
            ),
        )

        return redirect("home")

    return redirect(
        "meeting_room",
        meeting_id=meeting.id
    )

# =====================================================
# DELETE CREATED MEETING
# =====================================================

@login_required
def delete_created_meeting(request, meeting_id):

    meeting = get_object_or_404(
        Meeting,
        id=meeting_id,
        host=request.user,
    )

    if request.method == "POST":

        meeting.delete()

    return redirect("home")


# =====================================================
# REMOVE JOINED MEETING FROM HISTORY
# =====================================================

@login_required
def remove_joined_meeting(request, participant_id):

    participant = get_object_or_404(
        MeetingParticipant,
        id=participant_id,
        user=request.user,
    )

    if request.method == "POST":

        participant.delete()

    return redirect("home")