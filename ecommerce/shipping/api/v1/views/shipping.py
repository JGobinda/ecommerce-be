from rest_framework.response import Response

from ecommerce.commons.mixins.viewsets import ListCreateUpdateRetrieveViewSetMixin
from ecommerce.shipping.api.v1.serializers.shipping import ShippingDetailSerializer
from ecommerce.shipping.models import ShippingDetail


class ShippingDetailViewSet(ListCreateUpdateRetrieveViewSetMixin):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    queryset = ShippingDetail.objects.all()
    serializer_class = ShippingDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'detail': 'Submitted Successfully'
        })


