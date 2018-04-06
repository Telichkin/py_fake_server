from typing import List

import pytest
import requests

from py_fake_server import FakeServer


@pytest.mark.parametrize("method", ["get", "post", "delete", "patch"])
@pytest.mark.parametrize(["route", "status"],
                         [("/201", 201),
                          ("/204", 204),
                          ("/200", 200)])
def test_add_simple_handler(server: FakeServer, method: str, route: str, status: int):
    server. \
        on_(method, route). \
        response(status=status)

    response = requests.request(method, server.base_uri + route)
    assert response.status_code == status


@pytest.mark.parametrize("methods", [["get", "post"],
                                     ["post", "delete"],
                                     ["delete", "patch"],
                                     ["patch", "get"]])
@pytest.mark.parametrize(["routes", "statuses"],
                         [[["/same_route", "/same_route"], [201, 200]]])
def test_add_two_simple_handlers_with_same_route(server: FakeServer,
                                                 methods: List[str],
                                                 routes: List[str],
                                                 statuses: List[int]):
    server. \
        on_(methods[0], routes[0]). \
        response(status=statuses[0])

    server. \
        on_(methods[1], routes[1]). \
        response(status=statuses[1])

    response_0 = requests.request(methods[0], server.base_uri + routes[0])
    response_1 = requests.request(methods[1], server.base_uri + routes[1])
    assert response_0.status_code == statuses[0]
    assert response_1.status_code == statuses[1]


def test_handler_returns_body(server: FakeServer):
    server. \
        on_("get", "/try/body"). \
        response(status=200, body="Wow! So Body!")

    response = requests.get(server.base_uri + "/try/body")
    assert response.text == "Wow! So Body!"


def test_handler_returns_content_type(server: FakeServer):
    server. \
        on_("post", "/content"). \
        response(status=200, body='{"json": "try"}', content_type="application/json")

    response = requests.post(server.base_uri + "/content")
    assert response.headers["content-type"] == "application/json"


def test_handler_returns_headers(server: FakeServer):
    server. \
        on_("post", "/data"). \
        response(status=200, body="text", headers={"retry-after": "500"})

    response = requests.post(server.base_uri + "/data")
    assert response.headers["retry-after"] == "500"


def test_handler_exception_when_content_type_explicit_and_in_headers(server: FakeServer):
    with pytest.raises(AttributeError) as error:
        server. \
            on_("post", "/data"). \
            response(status=200, body="lol", content_type="text/plain", headers={"Content-Type": "text/plain"})

    assert str(error.value) == "Explicit Content-Type and Content-Type in headers in one response"


def test_handler_returns_cookies(server: FakeServer):
    server. \
        on_("get", "/users"). \
        response(status=200, body="lol", cookies={"token": "new_token"})

    response = requests.get(server.base_uri + "/users")
    assert response.cookies == {"token": "new_token"}


def test_handler_exception_when_cookies_explicit_and_in_headers(server: FakeServer):
    with pytest.raises(AttributeError) as error:
        server. \
            on_("get", "/movies/1"). \
            response(status=204, cookies={"token": "token"}, headers={"cookies": "token=token"})

    assert str(error.value) == "Explicit Cookies and Cookies in headers in one response"


def test_handler_set_for_many_times(server: FakeServer):
    server. \
        on_("get", "/users"). \
        response(status=200). \
        then(). \
        response(status=204)

    response_0 = requests.get(server.base_uri + "/users")
    response_1 = requests.get(server.base_uri + "/users")
    assert response_0.status_code == 200
    assert response_1.status_code == 204


def test_set_handler_many_times(server: FakeServer):
    server. \
        on_("get", "/users"). \
        response(status=204)

    server. \
        on_("get", "/users"). \
        response(status=200)

    response = requests.get(server.base_uri + "/users")
    assert response.status_code == 200


def test_handler_calls_many_times(server: FakeServer):
    server. \
        on_("patch", "/channels"). \
        response(status=204)

    response_0 = requests.patch(server.base_uri + "/channels")
    response_1 = requests.patch(server.base_uri + "/channels")
    assert response_0.status_code == 204
    assert response_1.status_code == 204


def test_handler_set_number_of_calls_explicitly(server: FakeServer):
    server. \
        on_("get", "/games"). \
        response(status=200).once()

    response_0 = requests.get(server.base_uri + "/games")
    response_1 = requests.get(server.base_uri + "/games")
    assert response_0.status_code == 200
    assert response_1.status_code == 500
    assert response_1.text == "Server has not responses for [GET] http://localhost:8081/games"
    assert response_1.headers["content-type"] == "text/plain"


def test_handler_two_responses_both_called_once(server: FakeServer):
    server. \
        on_("get", "/games"). \
        response(status=200).once(). \
        then(). \
        response(status=204).once()

    response_0 = requests.get(server.base_uri + "/games")
    response_1 = requests.get(server.base_uri + "/games")
    response_2 = requests.get(server.base_uri + "/games")
    assert response_0.status_code == 200
    assert response_1.status_code == 204
    assert response_2.status_code == 500
    assert response_2.text == "Server has not responses for [GET] http://localhost:8081/games"
    assert response_2.headers["content-type"] == "text/plain"


def test_handler_called_twice(server: FakeServer):
    server. \
        on_("post", "/songs"). \
        response(status=204).twice()

    response_0 = requests.post(server.base_uri + "/songs")
    response_1 = requests.post(server.base_uri + "/songs")
    response_2 = requests.post(server.base_uri + "/songs")
    assert response_0.status_code == 204
    assert response_1.status_code == 204
    assert response_2.status_code == 500
    assert response_2.text == "Server has not responses for [POST] http://localhost:8081/songs"
    assert response_2.headers["content-type"] == "text/plain"


def test_handler_called_nth_times(server: FakeServer):
    server. \
        on_("patch", "/songs"). \
        response(status=204)._3_times()

    response_0 = requests.patch(server.base_uri + "/songs")
    response_1 = requests.patch(server.base_uri + "/songs")
    response_2 = requests.patch(server.base_uri + "/songs")
    response_3 = requests.patch(server.base_uri + "/songs")
    assert response_0.status_code == 204
    assert response_1.status_code == 204
    assert response_2.status_code == 204
    assert response_3.status_code == 500
    assert response_3.text == "Server has not responses for [PATCH] http://localhost:8081/songs"
    assert response_3.headers["content-type"] == "text/plain"


def test_handler_called_nth_times_with_wrong_syntax(server: FakeServer):
    with pytest.raises(AttributeError) as error:
        server. \
            on_("post", "/plays"). \
            response(status=200, body="lol")._56_toims()

    assert str(error.value) == "'Endpoint' object has no attribute '_56_toims'"


def test_handler_called_one_time_other_syntax(server: FakeServer):
    server. \
        on_("get", "/plays"). \
        response(status=200, body="Wow!")._1_times()

    response_0 = requests.get(server.base_uri + "/plays")
    response_1 = requests.get(server.base_uri + "/plays")
    assert response_0.status_code == 200
    assert response_1.status_code == 500
    assert response_1.text == "Server has not responses for [GET] http://localhost:8081/plays"
    assert response_1.headers["content-type"] == "text/plain"


def test_missing_route_returns_500(server: FakeServer):
    response = requests.post(server.base_uri + "/missing_path")
    assert response.status_code == 500
    assert response.text == "Server has not responses for [POST] http://localhost:8081/missing_path"
    assert response.headers["content-type"] == "text/plain"


def test_handler_204_without_body(server: FakeServer):
    server. \
        on_("delete", "/user/1"). \
        response(status=204)

    response = requests.delete(server.base_uri + "/user/1")
    assert response.status_code == 204
    assert not response.content


def test_add_response_with_204_and_body_raise_exception(server: FakeServer):
    with pytest.raises(AttributeError) as error:
        server. \
            on_("delete", "/error"). \
            response(status=204, body="some body")

    assert str(error.value) == "status == 204 and body != None in one response"


def test_route_with_ending_slash(server: FakeServer):
    server. \
        on_("get", "/users/"). \
        response(status=200, body="Hello!")

    response = requests.get(server.base_uri + "/users/")
    assert response.status_code == 200
    assert response.text == "Hello!"


def test_json_in_response(server: FakeServer):
    (server.
        on_("get", "/json_response").
        response(status=200, json={"hello": "world"}))

    response = requests.get(server.base_uri + "/json_response")
    assert response.status_code == 200
    assert response.json() == {"hello": "world"}
    assert response.headers["Content-Type"] == "application/json"


def test_json_and_body_raise_exception(server: FakeServer):
    with pytest.raises(AttributeError) as error:
        (server.
            on_("post", "/error").
            response(status=200, body="Oops!", json={"oops": "I did it again"}))

    assert str(error.value) == "'body' and 'json' in one response"


def test_explicit_content_type_remove_application_json(server: FakeServer):
    (server.
        on_("patch", "/games").
        response(status=200, json={"change": "content-type"}, content_type="text/plain"))

    response = requests.patch(server.base_uri + "/games")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/plain"


def test_was_not_requested_with_slash_at_the_end(server: FakeServer):
    server.on_("get", "/slash").response(200)

    requests.get(server.base_uri + "/slash/")

    with pytest.raises(AssertionError):
        server.was_not_requested("get", "/slash/")
