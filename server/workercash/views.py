from django.shortcuts import render

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import WorkerCash


class WorkerCashCountAPIView(APIView):
    def post(self, request, *args, **kwargs):
        ip = request.data.get("ip", "")
        if not ip:
            return Response(
                {"error": "Invalid IP address"}, status=status.HTTP_400_BAD_REQUEST
            )

        workercash, _ = WorkerCash.objects.get_or_create(ip=ip)
        workercash.count += 1
        workercash.save()

        return Response({"message": "success"}, status=status.HTTP_200_OK)
