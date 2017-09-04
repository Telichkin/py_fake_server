from typing import Optional, Dict, Tuple

import falcon
from falcon_multipart.middleware import MultipartMiddleware
from webtest.http import StopableWSGIServer

from .endpoint import Endpoint
from .statistic import Statistic, RequestedParams


class FakeServer(falcon.API):
    def __init__(self, host: str, port: int):
        super().__init__(middleware=[MultipartMiddleware()])
        self.req_options = self._get_request_options()
        self._host: str = host
        self._port: int = port
        self._server: Optional[StopableWSGIServer] = None
        self._endpoints: Dict[Tuple[str, str], Endpoint] = {}
        self._statistics: Dict[Tuple[str, str], Statistic] = {}
        self.add_sink(self._handle_all)

    @staticmethod
    def _get_request_options():
        options = falcon.RequestOptions()
        options.auto_parse_qs_csv = False
        return options

    def _handle_all(self, request: falcon.Request, response: falcon.Response):
        route = (request.method.lower(), self.base_uri + request.path.rstrip("/"))
        endpoint = self._endpoints.get(route, None)
        if endpoint:
            self._set_response_attributes_from_endpoint(response, endpoint)
            endpoint.called()
        else:
            error_endpoint = Endpoint(request.method, self.base_uri + request.path).once()
            error_endpoint.called()
            self._set_response_attributes_from_endpoint(response, error_endpoint)

        self._update_statistics(request, route)

    @staticmethod
    def _set_response_attributes_from_endpoint(response: falcon.Response, endpoint: Endpoint):
        response.status = getattr(falcon, f"HTTP_{endpoint.status}")
        response.body = endpoint.body
        if endpoint.content_type:
            response.content_type = endpoint.content_type
        for header_name, header_value in endpoint.headers.items():
            response.set_header(header_name, header_value)
        for cookie_name, cookie_value in endpoint.cookies.items():
            response.set_cookie(cookie_name, cookie_value)

    def _update_statistics(self, request: falcon.Request, route: Tuple[str, str]):
        self._statistics.setdefault(route, Statistic(route[0], route[1]))
        statistic = self._statistics.get(route)
        statistic.requests.append(RequestedParams(cookies=request.cookies,
                                                  body=request.bounded_stream.read(),
                                                  content_type=request.content_type,
                                                  files=self._get_files(request),
                                                  headers=request.headers,
                                                  query_params=request.params))

    @staticmethod
    def _get_files(request: falcon.Request) -> Optional[Dict[str, bytes]]:
        files = {
            param_name: param_value.file.read()
            for param_name, param_value in request.params.items()
            if hasattr(param_value, "file")
        }

        return files if files else None

    @property
    def base_uri(self):
        return f"http://{self._host}:{self._port}"

    def start(self):
        self._server = StopableWSGIServer.create(self, host=self._host, port=self._port)

    def stop(self):
        self._server.shutdown()

    def clear(self):
        self._endpoints = {}
        self._statistics = {}

    def on_(self, method: str, url: str) -> Endpoint:
        new_endpoint = Endpoint(method.lower(), self.base_uri + url.rstrip("/"))
        self._endpoints[(new_endpoint.method, new_endpoint.url)] = new_endpoint
        return new_endpoint

    def was_requested(self, method: str, url: str) -> Statistic:
        route = (method.lower(), self.base_uri + url.rstrip("/"))
        self._statistics.setdefault(route, Statistic(route[0], route[1]))
        return self._statistics.get(route)

    def was_not_requested(self, method: str, url: str) -> Statistic:
        route = (method.lower(), self.base_uri + url)
        self._statistics.setdefault(route, Statistic(route[0], route[1]))
        statistic: Statistic = self._statistics.get(route)
        statistic.exactly_0_times()
        return statistic


def expect_that(server: FakeServer):
    return server
