import re
from typing import Optional, List, Dict

from py_fake_server.response import Response
from py_fake_server.route import Route


class Endpoint:
    def __init__(self, route: Route):
        self.method = route.method
        self.url = route.url
        self._recorded_responses: List[Response] = []
        self._error_response = Response(
            status=500,
            content_type="text/plain",
            body=f"Server has not responses for [{self.method.upper()}] {self.url}",
        )
        self._last_recorded_response_is_infinite = True

    def pop_response(self) -> Response:
        if not self._recorded_responses:
            return self._error_response

        if len(self._recorded_responses) == 1 and self._last_recorded_response_is_infinite:
            return self._recorded_responses[0]

        return self._recorded_responses.pop(0)

    def response(self, status: int, body: Optional[str] = None, content_type: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None,
                 json: Optional[Dict] = None) -> "Endpoint":

        response = Response(status, body, content_type, headers, cookies, json)
        self._recorded_responses.append(response)
        self._last_recorded_response_is_infinite = True

        return self

    def then(self) -> "Endpoint":
        return self

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
            self._recorded_responses.append(self._recorded_responses[0])

        self._last_recorded_response_is_infinite = False
        return self
