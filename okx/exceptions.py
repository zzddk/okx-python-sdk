# coding=utf-8


class OkxAPIException(Exception):
    """Raised when OKX returns an HTTP error or a non-zero business code."""

    def __init__(self, response, payload=None):
        self.code = 'None'
        self.message = 'System error'
        if payload is None:
            try:
                payload = response.json()
            except ValueError:
                self.message = 'Invalid JSON error message from Okx: {}'.format(response.text)
        if isinstance(payload, dict):
            if 'code' in payload.keys() and 'msg' in payload.keys():
                self.code = payload['code']
                self.message = payload['msg']
        elif payload is not None:
            self.message = 'Unexpected response payload: {!r}'.format(payload)

        self.status_code = response.status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return 'API Request Error(code=%s): %s' % (self.code, self.message)


class PermanentConnectionError(ConnectionError):
    """A connection failure that retrying the same endpoint cannot fix."""


class OkxRequestException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'OkxRequestException: %s' % self.message


class OkxParamsException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'OkxParamsException: %s' % self.message
