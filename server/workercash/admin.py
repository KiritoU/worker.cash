import pytz

from django.conf import settings
from django.utils import timezone
from django.contrib import admin

from .models import WorkerCash


def get_now_datetime():
    now = timezone.localtime(timezone.now(), timezone=pytz.timezone(settings.TIME_ZONE))

    return now


class WorkerCashAdmin(admin.ModelAdmin):
    list_display = ("ip", "count", "updated_at", "status")
    # list_filter = ("status",)
    search_fields = ["count", "ip", "user"]
    # prepopulated_fields = {"tag": ("number",)}

    def status(self, obj):
        now = get_now_datetime()
        delta = now - obj.updated_at
        return delta.seconds <= 2 * 60

    status.boolean = False
    status.short_description = "Status"


admin.site.register(WorkerCash, WorkerCashAdmin)
