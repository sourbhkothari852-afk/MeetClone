from django.contrib import admin

from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):

    # =====================================================
    # LIST DISPLAY
    # =====================================================

    list_display = (
        "title",
        "host",
        "meeting_code",
        "scheduled_at",
        "status",
        "created_at",
    )


    # =====================================================
    # FILTERS
    # =====================================================

    list_filter = (
        "status",
        "scheduled_at",
        "created_at",
    )


    # =====================================================
    # SEARCH
    # =====================================================

    search_fields = (
        "title",
        "meeting_code",
        "host__username",
        "host__email",
    )


    # =====================================================
    # DEFAULT ORDER
    # =====================================================

    ordering = (
        "-created_at",
    )