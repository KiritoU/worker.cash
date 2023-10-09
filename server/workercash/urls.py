from django.urls import path

from .views import WorkerCashCountAPIView

urlpatterns = [
    path(f"count/", WorkerCashCountAPIView.as_view(), name="worker_cash_count"),
]
