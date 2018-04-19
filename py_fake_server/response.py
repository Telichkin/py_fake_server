import json as json_lib
from typing import Optional, Dict


class Response:
    def __init__(self, status: int, body: Optional[str] = None, content_type: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None,
                 json: Optional[Dict] = None):
        if status == 204 and body is not None:
            raise AttributeError("status == 204 and body != None in one response")

        headers_names = [k.lower() for k in headers.keys()] if headers else []
        if content_type and "content-type" in headers_names:
            raise AttributeError("Explicit Content-Type and Content-Type in headers in one response")
        if cookies and "cookies" in headers_names:
            raise AttributeError("Explicit Cookies and Cookies in headers in one response")
        if body is not None and json is not None:
            raise AttributeError("'body' and 'json' in one response")

        if json is not None:
            content_type = content_type or "application/json"
            body = json_lib.dumps(json)

        self.status = status
        self.body = body
        self.content_type = content_type
        self.headers = headers or {}
        self.cookies = cookies or {}
