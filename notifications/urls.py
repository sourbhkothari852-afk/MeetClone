from django.urls import path

from .views import (
    notifications_view,
    mark_notification_read_view,
    mark_all_notifications_read_view,
    delete_notification_view,
)


urlpatterns = [

    # =====================================================
    # NOTIFICATIONS
    # =====================================================

    path(
        "",
        notifications_view,
        name="notifications",
    ),

    # =====================================================
    # MARK AS READ
    # =====================================================

    path(
        "<int:notification_id>/read/",
        mark_notification_read_view,
        name="mark_notification_read",
    ),

    # =====================================================
# MARK ALL NOTIFICATIONS AS READ
# =====================================================

path(
    "mark-all-read/",
    mark_all_notifications_read_view,
    name="mark_all_notifications_read",
),

# =====================================================
# DELETE NOTIFICATION
# =====================================================

path(
    "<int:notification_id>/delete/",
    delete_notification_view,
    name="delete_notification",
),

]