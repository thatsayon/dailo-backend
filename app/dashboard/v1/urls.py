from django.urls import path
from .views import (
    AppliedCreatorListAPIView,
    AppliedCreatorStatusUpdateAPIView,
)

urlpatterns = [
    path("applications/", AppliedCreatorListAPIView.as_view(), name="creator-application"),
    path("applications/<uuid:id>/status/", AppliedCreatorStatusUpdateAPIView.as_view(), name='application-status-update'),
]
