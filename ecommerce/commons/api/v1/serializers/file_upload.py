from rest_framework import serializers

from spark.commons.models import FileUpload
from spark.commons.serializers import DynamicFieldsModelSerializer


class FileUploadSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = FileUpload
        read_only_fields = ['uuid', 'file_name']
        fields = ['uuid', 'file', 'file_name']

    def get_fields(self):
        fields = super().get_fields()
        if self.request and self.request.method.lower() == 'get':
            fields['file'] = serializers.URLField(source='file_thumb')
        return fields
