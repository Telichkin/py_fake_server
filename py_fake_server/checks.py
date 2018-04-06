import json
from typing import Dict


class HeaderDoesNotExist:
    def __repr__(self):
        return "<HEADER DOES NOT EXIST>"


def with_cookies(request, current_requested_time, cookies: Dict[str, str]):
    assert cookies == request.cookies, \
        f"\nFor the {current_requested_time} time: with cookies {cookies}.\n" \
        f"But for the {current_requested_time} time: cookies was {request.cookies}."


def with_body(request, current_requested_time, body: str):
    actual_body = request.body.decode("utf-8", errors="skip")
    assert body == actual_body, \
        f"\nFor the {current_requested_time} time: with body {body.__repr__()}.\n" \
        f"But for the {current_requested_time} time: body was {actual_body.__repr__()}."


def with_json(request, current_requested_time, json_dict: Dict):
    body = json.dumps(json_dict, sort_keys=True)
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


def with_content_type(request, current_requested_time, content_type: str):
    actual_content_type = request.content_type
    assert content_type == actual_content_type, \
        f"\nFor the {current_requested_time} time: with content type {content_type.__repr__()}.\n" \
        f"But for the {current_requested_time} time: content type was {actual_content_type.__repr__()}."


def with_files(request, current_requested_time, files: Dict[str, bytes]):
    assert files == request.files, \
        f"\nFor the {current_requested_time} time: with files {files}.\n" \
        f"But for the {current_requested_time} time: files was {request.files}."


def with_headers(request, current_requested_time, headers: Dict[str, str]):
    actual_headers = request.headers
    expected_headers = {name.upper(): value for name, value in headers.items()}

    headers_diff = _get_headers_diff(expected_headers, actual_headers)
    assert not headers_diff, \
        f"\nFor the {current_requested_time} time: with headers contain {expected_headers}.\n" \
        f"But for the {current_requested_time} time: headers contained {headers_diff}."


def _get_headers_diff(expected_headers: Dict[str, str], actual_headers: Dict[str, str]) -> Dict[str, str]:
    headers_diff = {}

    for header_name, header_value in expected_headers.items():
        if header_name in actual_headers and header_value != actual_headers[header_name]:
            headers_diff[header_name] = actual_headers[header_name]
        elif header_name not in actual_headers:
            headers_diff[header_name] = HeaderDoesNotExist()

    return headers_diff


def with_query_params(request, current_requested_time, query_params: Dict[str, str]):
    assert query_params == request.query_params, \
        f"\nFor the {current_requested_time} time: with query params {query_params}.\n" \
        f"But for the {current_requested_time} time: query params was {request.query_params}."

