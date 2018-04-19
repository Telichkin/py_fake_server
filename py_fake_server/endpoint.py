import re
from typing import Optional, List, Dict

from py_fake_server.response import Response
from py_fake_server.route import Route


class Endpoint:
    def __init__(self, route: Route):
        self.method = route.method
        self.url = route.url
        self._responses: List[Response] = []
        self._last_response = None
        self._called_times: int = 0

    @property
    def status(self) -> int:
        return self._current_response.status

    @property
    def body(self) -> Optional[str]:
        return self._current_response.body

    @property
    def content_type(self) -> Optional[str]:
        return self._current_response.content_type

    @property
    def headers(self) -> Dict[str, str]:
        return self._current_response.headers

    @property
    def cookies(self) -> Dict[str, str]:
        return self._current_response.cookies

    @property
    def _current_response(self) -> Response:
        if self._called_times > len(self._responses) - 1:
            return self._last_response
        return self._responses[self._called_times]

    def response(self, status: int, body: Optional[str] = None, content_type: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None,
                 json: Optional[Dict] = None) -> "Endpoint":

        response = Response(status, body, content_type, headers, cookies, json)
        self._responses.append(response)
        self._last_response = response

        return self

    def then(self) -> "Endpoint":
        return self

    def called(self):
        self._called_times += 1

    def once(self) -> "Endpoint":
        return self._1_times()

    def twice(self) -> "Endpoint":
        return self._2_times()

    def __getattr__(self, item):
        times_pattern = r"^_(?P<number>\d+)_times$"
        regex_result = re.match(times_pattern, item)
        if regex_result:
            number = int(regex_result.groupdict()["number"])
            return lambda: self._times(number)
        raise AttributeError(f"'Endpoint' object has no attribute '{item}'")

    def _times(self, number: int) -> "Endpoint":
        for i in range(number - 1):
            self._responses.append(self._responses[-1])

        self._last_response = Response(
            status=500,
            content_type="text/plain",
            body=f"Server has not responses for [{self.method.upper()}] {self.url}"
        )
        return self
