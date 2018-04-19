import json
from typing import Dict

from py_fake_server.request import Request


class HeaderDoesNotExist:
    def __repr__(self):
        return "<HEADER DOES NOT EXIST>"


class BaseValidator:
    def validate(self, request: Request, current_requested_time: int):
        raise NotImplementedError


class WithCookies(BaseValidator):
    def __init__(self, cookies: Dict[str, str]):
        self.cookies = cookies

    def validate(self, request, current_requested_time):
        assert self.cookies == request.cookies, \
            f"\nFor the {current_requested_time} time: with cookies {self.cookies}.\n" \
            f"But for the {current_requested_time} time: cookies was {request.cookies}."


class WithBody(BaseValidator):
    def __init__(self, body: str):
        self.body = body

    def validate(self, request, current_requested_time):
        actual_body = request.body.decode("utf-8", errors="skip")
        assert self.body == actual_body, \
            f"\nFor the {current_requested_time} time: with body {self.body.__repr__()}.\n" \
            f"But for the {current_requested_time} time: body was {actual_body.__repr__()}."


class WithJson(BaseValidator):
    def __init__(self, json_dict: Dict):
        self.json = json_dict

    def validate(self, request, current_requested_time):
        body = json.dumps(self.json, sort_keys=True)
        actual_body = request.body.decode("utf-8", errors="skip")

        try:
            actual_json_dict = json.loads(actual_body)
        except json.JSONDecodeError:
            assert False, \
                f"\nFor the {current_requested_time} time: with json {body}.\n" \
                f"But for the {current_requested_time} time: json was corrupted {actual_body.__repr__()}."

        actual_body = json.dumps(actual_json_dict, sort_keys=True)
        assert body == actual_body, \
            f"\nFor the {current_requested_time} time: with json {body}.\n" \
            f"But for the {current_requested_time} time: json was {actual_body}."


class WithContentType(BaseValidator):
    def __init__(self, content_type: str):
        self.content_type = content_type

    def validate(self, request, current_requested_time):
        assert self.content_type == request.content_type, \
            f"\nFor the {current_requested_time} time: with content type {self.content_type.__repr__()}.\n" \
            f"But for the {current_requested_time} time: content type was {request.content_type.__repr__()}."


class WithFiles(BaseValidator):
    def __init__(self, files: Dict[str, bytes]):
        self.files = files

    def validate(self, request, current_requested_time):
        assert self.files == request.files, \
            f"\nFor the {current_requested_time} time: with files {self.files}.\n" \
            f"But for the {current_requested_time} time: files was {request.files}."


class WithHeaders(BaseValidator):
    def __init__(self, headers: Dict[str, str]):
        self.headers = {name.upper(): value for name, value in headers.items()}

    def validate(self, request, current_requested_time):
        actual_headers = request.headers
        headers_diff = self._get_headers_diff(actual_headers)

        assert not headers_diff, \
            f"\nFor the {current_requested_time} time: with headers contain {self.headers}.\n" \
            f"But for the {current_requested_time} time: headers contained {headers_diff}."

    def _get_headers_diff(self, actual_headers: Dict[str, str]) -> Dict[str, str]:
        headers_diff = {}

        for header_name, header_value in self.headers.items():
            if header_name in actual_headers and header_value != actual_headers[header_name]:
                headers_diff[header_name] = actual_headers[header_name]
            elif header_name not in actual_headers:
                headers_diff[header_name] = HeaderDoesNotExist()

        return headers_diff


class WithQueryParams(BaseValidator):
    def __init__(self, query_params: Dict[str, str]):
        self.query_params = query_params

    def validate(self, request, current_requested_time):
        assert self.query_params == request.query_params, \
            f"\nFor the {current_requested_time} time: with query params {self.query_params}.\n" \
            f"But for the {current_requested_time} time: query params was {request.query_params}."

