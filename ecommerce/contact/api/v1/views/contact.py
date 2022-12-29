from ecommerce.commons.mixins.viewsets import ListCreateRetrieveViewSetMixin
from ecommerce.contact.api.v1.serializers.contact import ContactSerializer
from ecommerce.contact.models import Contact


class ContactViewSet(ListCreateRetrieveViewSetMixin):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
