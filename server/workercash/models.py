from django.db import models


class WorkerCash(models.Model):
    ip = models.CharField(max_length=100)
    count = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("updated_at",)
