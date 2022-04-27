from typing import Optional, Dict, Union, List, Tuple

import falcon
from falcon_multipart.middleware import MultipartMiddleware
from webtest.http import StopableWSGIServer
from py_fake_server import statistic
from .utils import UtilsMonitoring
from py_fake_server.route import Route
from py_fake_server.endpoint import Endpoint
from py_fake_server.statistic import Statistic

import logging

logger = logging.getLogger(__name__)


class FakeServer(falcon.API):
    @UtilsMonitoring.io_display(input=True, output=False, level=logging.DEBUG)
    def __init__(self, host: str, port: int):
        super().__init__(middleware=[MultipartMiddleware()])
        self.req_options = self._get_request_options()
        self._host: str = host
        self._port: int = port
        self._server: Optional[StopableWSGIServer] = None
        self._endpoints: Dict[Route, Endpoint] = {}
        self._statistics: Dict[Route, Statistic] = {}
        self.add_sink(self._handle_all)

    @staticmethod
    def _get_request_options():
        options = falcon.RequestOptions()
        options.auto_parse_qs_csv = False
        return options

    def _handle_all(self, request: falcon.Request, response: falcon.Response):
        route = Route(request.method, self.base_uri, request.path)
        endpoint = self._endpoints.get(route, Endpoint(route, request.params))
        logger.debug(f"Checking {endpoint.params} vs {request.params}")
        if endpoint.params == request.params:
            self._set_response_attributes_from_endpoint(response, endpoint)
        else:
            response.status = getattr(falcon, f"HTTP_400")
        self._update_statistics(request, route)

    @staticmethod
    def _set_response_attributes_from_endpoint(
        response: falcon.Response, endpoint: Endpoint
    ):
        recorded_response = endpoint.pop_response()

        response.status = getattr(falcon, f"HTTP_{recorded_response.status}")
        response.body = recorded_response.body
        if recorded_response.content_type:
            response.content_type = recorded_response.content_type
        for header_name, header_value in recorded_response.headers.items():
            response.set_header(header_name, header_value)
        for cookie_name, cookie_value in recorded_response.cookies.items():
            response.set_cookie(cookie_name, cookie_value)

    def _update_statistics(self, request: falcon.Request, route: Route):
        self._statistics.setdefault(route, Statistic(route.method, route.url))
        statistic: Union[Statistic, None] = self._statistics.get(route)
        if statistic is None:
            logger.error(f"Uknown route, {route}, when getting statistic")
            raise ValueError(f"Uknown route: {route}")
        else:
            statistic.record_request(request)

    @property
    def base_uri(self):
        return f"http://{self._host}:{self._port}"

    def start(self):
        self._server = StopableWSGIServer.create(self, host=self._host, port=self._port)
        logger.info(f"Starting {__name__} on {self._host}:{self._port}")

    def stop(self):
        if self._server is not None:
            self._server.shutdown()
            logger.info(f"Stopping {__name__}")
        else:
            logger.warning(f"{__name__} is already stopped !")

    def clear(self):
        self._endpoints = {}
        self._statistics = {}

    @UtilsMonitoring.io_display(input=True, output=True, level=logging.DEBUG)
    def on_(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Union[str, List[str]]]] = None,
    ) -> Endpoint:
        route = Route(method, self.base_uri, url)
        new_endpoint = Endpoint(route, params)
        self._endpoints[route] = new_endpoint
        return new_endpoint

    @UtilsMonitoring.io_display(input=True, output=True, level=logging.DEBUG)
    def was_requested(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Union[str, List[str]]]] = None,
    ) -> Statistic:
        route = Route(method, self.base_uri, url)
        self._statistics.setdefault(route, Statistic(route.method, route.url))
        statistic: Union[Statistic, None] = self._statistics.get(route)
        if statistic is None:
            raise ValueError(f"Uknown route: {route}")
        return statistic

    @UtilsMonitoring.io_display(input=True, output=True, level=logging.DEBUG)
    def was_not_requested(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Union[str, List[str]]]] = None,
    ) -> Statistic:
        route = Route(method, self.base_uri, url)
        self._statistics.setdefault(route, Statistic(route.method, route.url))
        statistic: Union[Statistic, None] = self._statistics.get(route)
        if statistic is None:
            logger.error(f"Uknown route: {route} when getting statistic")
            raise ValueError(f"Uknown route: {route}")
        statistic.exactly_0_times()
        return statistic


@UtilsMonitoring.io_display(input=True, output=True, level=logging.DEBUG)
def expect_that(expectation: Union[FakeServer, Statistic]):
    if isinstance(expectation, FakeServer):
        return expectation
    else:
        return expectation.check()
