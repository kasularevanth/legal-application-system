from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    """
    List all notifications for the authenticated user
    """
    # TODO: Implement actual notification listing
    return Response([], status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_read(request, notification_id):
    """
    Mark a notification as read
    """
    # TODO: Implement marking notification as read
    return Response({"status": "success"}, status=status.HTTP_200_OK)