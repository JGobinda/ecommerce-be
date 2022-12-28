from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination, _positive_int
from rest_framework.response import Response


class LimitZeroNoResultsPagination(LimitOffsetPagination):
    max_limit = 50

    def get_limit(self, request):
        if self.limit_query_param:
            try:
                return _positive_int(
                    request.query_params[self.limit_query_param],
                    strict=False,
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError):
                pass

        return self.default_limit

    def get_paginated_response(self, data):
        return Response(OrderedDict([  # changing this because of special request from mobile team
            ('page', {'count': self.count,
                      'next': self.get_next_link(),
                      'previous': self.get_previous_link(),
                      'limit': self.limit,
                      'offset': self.offset
                      }),
            ('results', data)
        ]))
