from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .models import Notification


@login_required
def notifications_view(request):

    notifications = Notification.objects.filter(
        recipient=request.user
    )

    unread_count = notifications.filter(
        is_read=False
    ).count()

    return render(
        request,
        "notifications/notifications.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


# =====================================================
# MARK NOTIFICATION AS READ
# =====================================================

@login_required
def mark_notification_read_view(request, notification_id):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user,
    )

    notification.is_read = True

    notification.save(
        update_fields=["is_read"]
    )

    return redirect("notifications")


# =====================================================
# MARK ALL NOTIFICATIONS AS READ
# =====================================================

@login_required
def mark_all_notifications_read_view(request):

    Notification.objects.filter(
        recipient=request.user,
        is_read=False,
    ).update(
        is_read=True
    )

    return redirect("notifications")


# =====================================================
# DELETE NOTIFICATION
# =====================================================

@login_required
def delete_notification_view(
    request,
    notification_id
):

    # Only allow POST requests
    if request.method == "POST":

        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user,
        )

        notification.delete()

    return redirect(
        "notifications"
    )