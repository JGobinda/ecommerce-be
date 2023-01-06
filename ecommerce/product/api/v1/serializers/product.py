from ecommerce.commons.api.v1.serializers.file_upload import FileUploadSerializer
from ecommerce.commons.models import FileUpload
from ecommerce.commons.serializers import DynamicFieldsModelSerializer
from ecommerce.product.api.v1.serializers.category import CategorySerializer
from ecommerce.product.models import Product
from rest_framework import serializers


class ProductSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'in_stock', 'code', 'base_price', 'discount_price', 'quantity',
                  'sold_quantity', 'featured']

    def get_fields(self):
        fields = super(ProductSerializer, self).get_fields()
        view = self.context.get('view')
        if view and view.action in ['retrieve', 'list']:
            fields['category'] = CategorySerializer(fields=['uuid', 'title'], many=True)
            fields['images'] = serializers.SerializerMethodField()
        return fields

    def get_images(self, obj):
        request = self.context.get('request')
        image_uuids = obj.product_product_images.values_list('image__uuid', flat=True)
        return FileUploadSerializer(FileUpload.objects.filter(uuid__in=image_uuids),
                                    context={
                                        'request': request
                                    },
                                    many=True).data
