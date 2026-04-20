from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

class ApplyCreatorAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        return Response({

        })

