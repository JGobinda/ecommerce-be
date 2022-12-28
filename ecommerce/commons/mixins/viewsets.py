# pylint: disable=C0330 # to remove Wrong hanging indentation before block!! This was issue from pylint

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class ListRetrieveUpdateViewSetMixin(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet
):
    pass


class ListCreateUpdateViewSetMixin(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet
):
    pass


class ListCreateUpdateRetrieveViewSetMixin(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    pass


class UpdateRetrieveViewSetMixin(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    pass


class ListCreateRetrieveViewSetMixin(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    pass


class CreateViewSetMixin(
    mixins.CreateModelMixin,
    GenericViewSet
):
    pass


class ListViewSetMixin(
    mixins.ListModelMixin,
    GenericViewSet
):
    pass


class ListCreateViewSetMixin(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    pass


class ListCreateDestroyViewSetMixin(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    pass


class ListRetrieveViewSetMixin(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    pass


class RetrieveViewSetMixin(
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    pass


class RetrieveUpdateDestroyViewSetMixin(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    pass


class UpdateViewSetMixin(
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    pass


class RetrieveUpdateViewSetMixin(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet
):
    pass


class ListRetrieveUpdateDestroyViewSetMixin(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    pass


class ListUpdateViewSetMixin(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet
):
    pass
