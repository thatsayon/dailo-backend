from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics

from django_filters.rest_framework import DjangoFilterBackend

from app.creator.models import CreatorApplication

from app.dashboard.services.creator_approval_service import (
    update_creator_application_status,
)
from .serializers import (
    CreatorApplicationListSerializer,
    CreatorApplicationStatusSerializer
)
from .filters import CreatorApplicationFilter

class AppliedCreatorListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CreatorApplicationListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CreatorApplicationFilter

    def get_queryset(self):
        queryset = CreatorApplication.objects.select_related(
            "user"
        ).order_by("-created_at")

        status = self.request.query_params.get("status")

        if not status:
            queryset = queryset.filter(
                status=CreatorApplication.Status.PENDING
            )

        return queryset


class AppliedCreatorStatusUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CreatorApplicationStatusSerializer
    queryset = CreatorApplication.objects.select_related("user")
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        application = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_creator_application_status(
            application=application,
            **serializer.validated_data
        )

        return Response({
            "message": "Application status updated",
            "status": application.status
        })


