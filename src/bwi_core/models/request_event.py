class RequestEvent:
    def __init__(self, lambda_event_object):
        self.query_string_params = lambda_event_object.get('queryStringParameters', {}) or {}
        self.path_params = lambda_event_object.get('pathParameters', {}) or {}
        self.headers = lambda_event_object.get('headers', {}) or {}
        self.auth = self.headers.get('Authorization')

    def get_query_param(self, param):
        return self.query_string_params.get(param)

    def get_path_param(self, param):
        return self.path_params.get(param)

    def add_auth_requirement(self, token_val):
        self.auth_requirement = token_val

    def passes_auth(self):
        return self.auth_requirement == self.auth
