from django.urls import path

from .views import (
    create_meeting_view,
    meeting_detail_view,
    join_meeting_view,
    meeting_room_view,
    end_meeting_view,
    cancel_meeting_view,
    leave_meeting_view,
    delete_created_meeting,
    remove_joined_meeting,
)


urlpatterns = [

    # =====================================================
    # CREATE MEETING
    # =====================================================

    path(
        "create/",
        create_meeting_view,
        name="create_meeting",
    ),


    # =====================================================
    # JOIN MEETING
    # =====================================================

    path(
        "join/",
        join_meeting_view,
        name="join_meeting",
    ),


    # =====================================================
    # MEETING DETAIL
    # =====================================================

    path(
        "<int:meeting_id>/",
        meeting_detail_view,
        name="meeting_detail",
    ),


    # =====================================================
    # MEETING ROOM
    # =====================================================

    path(
        "<int:meeting_id>/room/",
        meeting_room_view,
        name="meeting_room",
    ),


    # =====================================================
    # END MEETING
    # =====================================================

    path(
        "<int:meeting_id>/end/",
        end_meeting_view,
        name="end_meeting",
    ),

    # =====================================================
# CANCEL MEETING
# =====================================================

path(
    "<int:meeting_id>/cancel/",
    cancel_meeting_view,
    name="cancel_meeting",
),


# =====================================================
# LEAVE MEETING
# =====================================================

path(
    "<int:meeting_id>/leave/",
    leave_meeting_view,
    name="leave_meeting",
),

    # =====================================================
    # DELETE CREATED MEETING
    # =====================================================

    path(
        "<int:meeting_id>/delete/",
        delete_created_meeting,
        name="delete_created_meeting",
    ),


    # =====================================================
    # REMOVE JOINED MEETING FROM HISTORY
    # =====================================================

    path(
        "history/<int:participant_id>/remove/",
        remove_joined_meeting,
        name="remove_joined_meeting",
    ),




]