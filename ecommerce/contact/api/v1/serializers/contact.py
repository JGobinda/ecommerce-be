from ecommerce.commons.serializers import DynamicFieldsModelSerializer
from ecommerce.contact.models import Contact


class ContactSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Contact
        fields = ['uuid', 'name', 'email', 'subject', 'message']
