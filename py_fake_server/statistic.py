import re
from typing import Optional, List, Callable, Dict


class RequestedParams:
    def __init__(self, cookies: Optional[Dict[str, str]], body: Optional[bytes], content_type: Optional[str],
                 files: Optional[Dict[str, bytes]], headers: Optional[Dict[str, str]]):
        self.cookies = cookies
        self.body = body
        self.content_type = content_type
        self.files = files
        self.headers = headers


class HeaderDoesNotExist:
    def __repr__(self):
        return "<HEADER DOES NOT EXIST>"


class Statistic:
    def __init__(self, method: str, url: str):
        self.method: str = method
        self.url: str = url
        self.requests: List[RequestedParams] = []
        self._current_request_index: Optional[int] = None
        self._number_of_requests_not_specify = True
        self._error_messages: List[str] = [f"Expect that server was requested with [{method.upper()}] {url}."]

    @property
    def requested_times(self):
        return len(self.requests)

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

    def exactly_once(self) -> "Statistic":
        return self.exactly_1_times()

    def exactly_twice(self) -> "Statistic":
        return self.exactly_2_times()

    def _exactly_times(self, expected_requested_times: int) -> Callable[[], "Statistic"]:
        self._number_of_requests_not_specify = False
        if expected_requested_times != self.requested_times:
            self._error_messages.append(f" {expected_requested_times} times.\n"
                                        f"But server was requested {self.requested_times} times.")
            self._raise_assertion()
        return lambda: self

    def for_the_first_time(self) -> "Statistic":
        return self.for_the_1_time()

    def for_the_second_time(self) -> "Statistic":
        return self.for_the_2_time()

    def _for_the_time(self, times: int) -> Callable[[], "Statistic"]:
        if self.requested_times < times:
            self._error_messages.append(f" At least {times} times.\n"
                                        f"But server was requested {self.requested_times} times.")
            self._raise_assertion()
        else:
            self._current_request_index = times - 1
            return lambda: self

    def with_cookies(self, cookies: Dict[str, str]) -> "Statistic":
        actual_cookies = self.get_current_request().cookies
        if cookies != actual_cookies:
            requested_time = self._current_request_index + 1
            self._error_messages.append(f"\nFor the {requested_time} time: with cookies {cookies}.\n"
                                        f"But for the {requested_time} time: cookies was {actual_cookies}.")
        return self

    def with_body(self, body: str) -> "Statistic":
        actual_body = self.get_current_request().body.decode("utf-8", errors="skip")
        if body != actual_body:
            requested_time = self._current_request_index + 1
            self._error_messages.append(f"\nFor the {requested_time} time: with body {body.__repr__()}.\n"
                                        f"But for the {requested_time} time: body was {actual_body.__repr__()}.")
        return self

    def with_content_type(self, content_type: str) -> "Statistic":
        actual_content_type = self.get_current_request().content_type
        if content_type != actual_content_type:
            requested_time = self._current_request_index + 1
            self._error_messages.append(
                f"\nFor the {requested_time} time: with content type {content_type.__repr__()}.\n"
                f"But for the {requested_time} time: content type was {actual_content_type.__repr__()}."
            )
        return self

    def with_files(self, files: Dict[str, bytes]) -> "Statistic":
        actual_files = self.get_current_request().files
        if files != actual_files:
            requested_time = self._current_request_index + 1
            self._error_messages.append(f"\nFor the {requested_time} time: with files {files}.\n"
                                        f"But for the {requested_time} time: files was {actual_files}.")
        return self

    def with_headers(self, headers: Dict[str, str]) -> "Statistic":
        actual_headers = self.get_current_request().headers
        expected_headers = {name.upper(): value for name, value in headers.items()}

        headers_diff = self._get_headers_diff(expected_headers, actual_headers)
        if headers_diff:
            requested_time = self._current_request_index + 1
            self._error_messages.append(f"\nFor the {requested_time} time: with headers contain {expected_headers}.\n"
                                        f"But for the {requested_time} time: headers contained {headers_diff}.")
        return self

    @staticmethod
    def _get_headers_diff(expected_headers: Dict[str, str], actual_headers: Dict[str, str]) -> Dict[str, str]:
        headers_diff = {}

        for header_name, header_value in expected_headers.items():
            if header_name in actual_headers and header_value != actual_headers[header_name]:
                headers_diff[header_name] = actual_headers[header_name]
            elif header_name not in actual_headers:
                headers_diff[header_name] = HeaderDoesNotExist()

        return headers_diff

    def get_current_request(self) -> RequestedParams:
        if self._current_request_index is None:
            raise AttributeError("You should specify concrete request for check with 'for_the_<any_number>_time'")
        return self.requests[self._current_request_index]

    def check(self):
        if not self.requested_times and self._number_of_requests_not_specify:
            self._error_messages.append("\nBut server was requested 0 times.")

        if self.errors_exist:
            self._raise_assertion()
        else:
            self._clean_state()

    @property
    def errors_exist(self):
        return len(self._error_messages) > 1

    def _raise_assertion(self):
        error_message = "".join(self._error_messages)
        self._clean_state()
        raise AssertionError(error_message)

    def _clean_state(self):
        self._error_messages = self._error_messages[0:1]
        self._number_of_requests_not_specify = True
        self._current_request_index = None
