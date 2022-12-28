from user_agents import parse


class CustomUserAgentMiddleWare:
    # we can take reference of django-user_agents to enhance parsing using the cache
    # reference link:==> https://github.com/selwin/django-user_agents
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    @staticmethod
    def process_request(request):
        # do all the parsing here
        # and add parsed information in request.user_agent

        ua_string = request.META.get('HTTP_USER_AGENT', '')
        if not isinstance(ua_string, str):
            ua_string = ua_string.decode('utf-8', 'ignore')
        user_agent = parse(ua_string)
        request.user_agent = user_agent
