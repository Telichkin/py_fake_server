import re
from functools import wraps
from typing import Optional, List, Callable, Dict

from py_fake_server.checks import with_cookies, with_body, with_json, with_content_type, with_files, with_headers, \
    with_query_params


class RequestedParams:
    def __init__(self, cookies: Optional[Dict[str, str]], body: Optional[bytes], content_type: Optional[str],
                 files: Optional[Dict[str, bytes]], headers: Optional[Dict[str, str]],
                 query_params: Optional[Dict[str, str]]):
        self.cookies = cookies
        self.body = body
        self.content_type = content_type
        self.files = files
        self.headers = headers
        self.query_params = query_params


def check(method):
    @wraps(method)
    def decorator(self, *args, **kwargs):
        try:
            method(self, *args, **kwargs)
        except AssertionError as error:
            self._error_messages.append(str(error))
        return self
    return decorator


class Statistic:
    def __init__(self, method: str, url: str):
        self.method: str = method
        self.url: str = url
        self.requests: List[RequestedParams] = []
        self._current_request_index: Optional[int] = None
        self._number_of_requests_not_specify: bool = True
        self._error_messages: List[str] = [f"Expect that server was requested with [{method.upper()}] {url}."]

    @property
    def requested_times(self) -> int:
        return len(self.requests)

    @property
    def current_requested_time(self) -> int:
        return self._current_request_index + 1

    def exactly_once(self) -> "Statistic":
        return self.exactly_1_times()

    def exactly_twice(self) -> "Statistic":
        return self.exactly_2_times()

    def for_the_first_time(self) -> "Statistic":
        return self.for_the_1_time()

    def for_the_second_time(self) -> "Statistic":
        return self.for_the_2_time()

    def __getattr__(self, item):
        exactly_times_pattern = r"^exactly_(?P<number>\d+)_times$"
        exactly_times_result = re.match(exactly_times_pattern, item)
        if exactly_times_result:
            number = int(exactly_times_result.groupdict()["number"])
            return self._exactly_times(number)

        for_the_time_pattern = r"^for_the_(?P<number>\d+)_time$"
        for_the_time_result = re.match(for_the_time_pattern, item)
        if for_the_time_result:
            number = int(for_the_time_result.groupdict()["number"])
            return self._for_the_time(number)

        raise AttributeError(f"'Statistic' object has no attribute '{item}'")

    def _exactly_times(self, expected_requested_times: int) -> Callable[[], "Statistic"]:
        self._number_of_requests_not_specify = False
        if expected_requested_times != self.requested_times:
            self._error_messages.append(f" {expected_requested_times} times.\n"
                                        f"But server was requested {self.requested_times} times.")
            self._raise_assertion()
        return lambda: self

    def _for_the_time(self, times: int) -> Callable[[], "Statistic"]:
        if self.requested_times < times:
            self._error_messages.append(f" At least {times} times.\n"
                                        f"But server was requested {self.requested_times} times.")
            self._raise_assertion()
        else:
            self._current_request_index = times - 1
            return lambda: self

    @check
    def with_cookies(self, cookies: Dict[str, str]) -> "Statistic":
        with_cookies(self.current_request, self.current_requested_time, cookies)

    @check
    def with_body(self, body: str) -> "Statistic":
        with_body(self.current_request, self.current_requested_time, body)

    @check
    def with_json(self, json_dict: dict) -> "Statistic":
        with_json(self.current_request, self.current_requested_time, json_dict)

    @check
    def with_content_type(self, content_type: str) -> "Statistic":
        with_content_type(self.current_request, self.current_requested_time, content_type)

    @check
    def with_files(self, files: Dict[str, bytes]) -> "Statistic":
        with_files(self.current_request, self.current_requested_time, files)

    @check
    def with_headers(self, headers: Dict[str, str]) -> "Statistic":
        with_headers(self.current_request, self.current_requested_time, headers)

    @check
    def with_query_params(self, query_params: Dict[str, str]) -> "Statistic":
        with_query_params(self.current_request, self.current_requested_time, query_params)

    @property
    def current_request(self) -> RequestedParams:
        if self._current_request_index is None:
            raise RuntimeError("You should specify concrete request for check with 'for_the_<any_number>_time'")
        return self.requests[self._current_request_index]

    def check(self) -> bool:
        if not self.requested_times and self._number_of_requests_not_specify:
            self._error_messages.append("\nBut server was requested 0 times.")

        if self.errors_exist:
            self._raise_assertion()
        else:
            self._clean_state()
            return True

    @property
    def errors_exist(self) -> bool:
        return len(self._error_messages) > 1

    def _raise_assertion(self):
        error_message = "".join(self._error_messages)
        self._clean_state()
        raise AssertionError(error_message)

    def _clean_state(self):
        self._error_messages = self._error_messages[0:1]
        self._number_of_requests_not_specify = True
        self._current_request_index = None
