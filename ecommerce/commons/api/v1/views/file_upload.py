from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from spark.commons.api.v1.serializers.file_upload import FileUploadSerializer


class FileViewSet(GenericViewSet):
    serializer_class = FileUploadSerializer
    parser_classes = [MultiPartParser]

    @action(detail=False, methods=['post'])
    def upload(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({
            'uuid': instance.uuid.hex,
            'url': instance.file_thumb,
            'name': instance.file_name,
            'message': 'File uploaded',
        }, status=status.HTTP_201_CREATED)
