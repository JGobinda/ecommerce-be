from django.db.models import Sum, F, Count, Avg, Q

from ecommerce.commons.api.v1.serializers.file_upload import FileUploadSerializer
from ecommerce.commons.models import FileUpload
from ecommerce.commons.serializers import DynamicFieldsModelSerializer
from ecommerce.product.api.v1.serializers.category import CategorySerializer
from ecommerce.product.models import Product, ProductRating
from rest_framework import serializers

from ecommerce.wishlist.models import WishList


class ProductSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Product
        fields = ['uuid', 'name', 'description', 'category', 'in_stock', 'code', 'base_price', 'discount_price',
                  'quantity',
                  'sold_quantity', 'featured', 'total_ratings']

    def get_fields(self):
        fields = super(ProductSerializer, self).get_fields()
        view = self.context.get('view')
        if view and view.action in ['retrieve', 'list', 'featured_products', 'latest_products',
                                    'top_discount_products', 'trending_products', 'related_products', 'recent_orders',
                                    'get_wished_products']:
            fields['category'] = CategorySerializer(fields=['uuid', 'title'], many=True)
            fields['images'] = serializers.SerializerMethodField()
            fields['features'] = serializers.SerializerMethodField()
            fields['ratings'] = serializers.SerializerMethodField()
            fields['in_wishlist'] = serializers.SerializerMethodField()
        if view and view.action in ['top_discount_products']:
            fields['discount_per'] = serializers.SerializerMethodField()
        if view and view.action in ['update_product_rating']:
            fields.clear()
            fields['flag'] = serializers.BooleanField(default=True)
        if view and view.action in ['get_product_ratings']:
            fields.clear()
            fields['overall_ratings'] = serializers.SerializerMethodField()
        return fields

    def get_images(self, obj):
        request = self.context.get('request')
        image_uuids = obj.product_product_images.values_list('image__uuid', flat=True)
        return FileUploadSerializer(FileUpload.objects.filter(uuid__in=image_uuids),
                                    context={
                                        'request': request
                                    },
                                    many=True).data

    def get_features(self, obj):
        features = obj.product_product_features.all()
        features_list = [{"title": feature.title} for feature in features]
        return features_list

    def get_discount_per(self, obj):
        if obj.base_price == 0:
            return 0
        return round((obj.discount_price / obj.base_price) * 100, 0)

    def get_ratings(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            try:
                product_rating_object = ProductRating.objects.get(product=obj, user=request.user)
                product_rating_uuid = product_rating_object.uuid
                product_rating = product_rating_object.ratings
            except ProductRating.DoesNotExist:
                product_rating_uuid = False
                product_rating = 1
        else:
            product_rating_uuid = False
            product_rating = 1
        return {
            'rating': product_rating,
            'product_rating_uuid': product_rating_uuid
        }

    def get_in_wishlist(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        try:
            wishlist_object = WishList.objects.get(user=request.user, product=obj)
            return wishlist_object.uuid
        except WishList.DoesNotExist:
            return False
        except WishList.MultipleObjectsReturned:
            return False

    def get_overall_ratings(self, obj):
        product = self.context.get('product')
        product_ratings = ProductRating.objects.filter(product=product).count()
        product_rating_queryset = ProductRating.objects.filter(product=product).aggregate(
            one=Count('id', filter=Q(ratings=1)),
            two=Count('id', filter=Q(ratings=2)),
            three=Count('id', filter=Q(ratings=3)),
            four=Count('id', filter=Q(ratings=4)),
            five=Count('id', filter=Q(ratings=5)),
        )
        if product_ratings == 0:
            product_ratings = 1
        data = {
            'total': product_ratings,
            'one': round(product_rating_queryset['one'] / product_ratings, 2) * 100,
            'two': round(product_rating_queryset['two'] / product_ratings, 2) * 100,
            'three': round(product_rating_queryset['three'] / product_ratings, 2) * 100,
            'four': round(product_rating_queryset['four'] / product_ratings, 2) * 100,
            'five': round(product_rating_queryset['five'] / product_ratings, 2) * 100,
            'one_count': product_rating_queryset['one'],
            'two_count': product_rating_queryset['two'],
            'three_count': product_rating_queryset['three'],
            'four_count': product_rating_queryset['four'],
            'five_count': product_rating_queryset['five']
        }
        return data


class ProductRatingSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ProductRating
        fields = ['uuid', 'product', 'ratings']

    def get_fields(self):
        fields = super(ProductRatingSerializer, self).get_fields()
        request = self.context.get('request')
        if request and request.method.lower() in ['get']:
            fields['product'] = ProductSerializer(fields=['uuid', 'name'])
        if request and request.method.lower() in ['post']:
            fields['product'] = serializers.SlugRelatedField(slug_field='uuid', queryset=Product.objects.all())
        if request and request.method.lower() in ['put', 'patch']:
            fields.pop('product')
        return fields

    def validate(self, attrs):
        view = self.context.get('view')
        request = self.context.get('request')
        ratings = attrs.get('ratings')

        if view and view.action in ['create']:
            product = attrs.get('product')
            if ProductRating.objects.filter(user=request.user, product=product).exists():
                raise serializers.ValidationError({
                    'detail': 'You cannot rate again.'
                })

        if view and view.action in ['update', 'partial_update']:
            obj = self.context.get('object')
            if not ProductRating.objects.filter(user=request.user, product=obj.product).exists():
                raise serializers.ValidationError({
                    'detail': 'rate this product first'
                })
            if ratings > 5:
                raise serializers.ValidationError({
                    'detail': 'You cannot rate a product more than 5'
                })
            if ratings < 1:
                raise serializers.ValidationError({
                    'detail': 'You cannot rate a product less than 1'
                })
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        product = validated_data.get('product')
        instance = super(ProductRatingSerializer, self).create(validated_data)
        product_ratings_object = ProductRating.objects.filter(product=product)
        product_ratings_count = product_ratings_object.aggregate(rating=Sum('ratings') / Count('id'))['rating']
        product.total_ratings = product_ratings_count
        product.save()
        return instance

    def update(self, instance, validated_data):
        instance = super(ProductRatingSerializer, self).update(instance=instance, validated_data=validated_data)
        product = instance.product
        product_ratings_object = ProductRating.objects.filter(product=product)
        product_ratings_count = product_ratings_object.aggregate(rating=Avg('ratings'))['rating']
        product.total_ratings = product_ratings_count
        product.save()
        return instance
