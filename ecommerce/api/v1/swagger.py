"""
v1 view for spark swagger
"""
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from rest_framework_swagger import renderers


class SwaggerSchemaView(APIView):
    """
    Swagger Schema View class
    """
    renderer_classes = [
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer,
    ]
    permission_classes = []

    def get(self, request):
        """
        :param request: request object
        :return: schema response
        """
        generator = SchemaGenerator(title='Hekto', urlconf='ecommerce.api.v1.urls', url="/api/v1/")
        schema = generator.get_schema(request=request)
        return Response(schema)
