import json


class Request:
    def __str__(self):
        return str(self.to_dict())

    def __init__(self, command_id, method: str, params: dict):
        self.id = command_id
        self.method = method
        self.params = params

    def is_valid(self):
        return self.method

    def is_notification(self):
        return not self.id

    def to_dict(self) -> dict:
        if self.id:
            return {
                'method': self.method,
                'params': self.params,
                'jsonrpc': '2.0',
                'id': self.id,
            }
        return {
            'method': self.method,
            'params': self.params,
            'jsonrpc': '2.0'
        }


class Response:
    def __str__(self):
        return str(self.to_dict())

    def __init__(self, command_id: str, result=None, error=None):
        self.id = command_id
        self.result = result
        self.error = error

    def is_valid(self):
        return self.id

    def is_error(self):
        return self.error

    def is_message(self):
        return self.result

    def to_dict(self) -> dict:
        if self.is_error():
            return {
                'error': self.error,
                'jsonrpc': '2.0',
                'id': self.id,
            }

        if self.is_message():
            return {
                'result': self.result,
                'jsonrpc': '2.0',
                'id': self.id,
            }

        return dict()


# rpc functions
def parse_response_or_request(data: str) -> (Request, Response):
    resp_req = json.loads(data)

    if 'method' in resp_req:
        params = None
        if 'params' in resp_req:
            params = resp_req['params']

        command_id = None
        if 'id' in resp_req:
            command_id = resp_req['id']

        return Request(command_id, resp_req['method'], params), None

    if 'result' in resp_req:
        return None, Response(resp_req['id'], resp_req['result'], None)

    if 'error' in resp_req:
        return None, Response(resp_req['id'], None, resp_req['error'])

    return None, None
