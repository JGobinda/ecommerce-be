from ecommerce.commons.api.v1.serializers.file_upload import FileUploadSerializer
from ecommerce.commons.models import FileUpload
from ecommerce.commons.serializers import DynamicFieldsModelSerializer
from ecommerce.product.api.v1.serializers.category import CategorySerializer
from ecommerce.product.models import Product
from rest_framework import serializers


class ProductSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Product
        fields = ['uuid', 'name', 'description', 'category', 'in_stock', 'code', 'base_price', 'discount_price',
                  'quantity',
                  'sold_quantity', 'featured', 'ratings']

    def get_fields(self):
        fields = super(ProductSerializer, self).get_fields()
        view = self.context.get('view')
        if view and view.action in ['retrieve', 'list', 'featured_products', 'latest_products']:
            fields['category'] = CategorySerializer(fields=['uuid', 'title'], many=True)
            fields['images'] = serializers.SerializerMethodField()
        if view and view.action in ['update_product_rating']:
            fields.clear()
            fields['flag'] = serializers.BooleanField(default=True)
        return fields

    def validate(self, attrs):
        view = self.context.get('view')
        flag = attrs.get('flag')
        if view and view.action in ['update_product_rating']:
            product = self.context.get('object')
            if product.ratings >= 5 and flag:
                raise serializers.ValidationError({
                    'detail': 'You cannot rate a product more than 5'
                })
            if product.ratings <=1 and not flag:
                raise serializers.ValidationError({
                    'detail': 'You cannot rate a product less than 1'
                })
        return attrs

    def get_images(self, obj):
        request = self.context.get('request')
        image_uuids = obj.product_product_images.values_list('image__uuid', flat=True)
        return FileUploadSerializer(FileUpload.objects.filter(uuid__in=image_uuids),
                                    context={
                                        'request': request
                                    },
                                    many=True).data
