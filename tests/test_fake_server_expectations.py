import pytest
import requests

from py_fake_server import FakeServer, expect_that


def test_expect_that_return_fake_server(server: FakeServer):
    assert expect_that(server) == server


def test_has_requested_raise_assertion(server: FakeServer):
    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("post", "/games"). \
            check()

    assert str(error.value) == "Expect that server was requested with [POST] http://localhost:8081/games.\n" \
                               "But server was requested 0 times."


@pytest.mark.parametrize("method", ["get", "post", "patch", "delete"])
def test_has_requested_not_raise_assertion_when_requested(server: FakeServer, method):
    requests.request(method, server.base_uri + "/users")

    expect_that(server). \
        was_requested(method, "/users"). \
        check()


@pytest.mark.parametrize("method", ["get", "post", "patch", "delete"])
def test_has_requested_raise_exception_once(server: FakeServer, method):
    requests.request(method, server.base_uri + "/images/1")
    requests.request(method, server.base_uri + "/images/1")

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested(method, "/images/1"). \
            exactly_once(). \
            check()

    assert str(error.value) == (f"Expect that server was requested with [{method.upper()}] "
                                f"http://localhost:8081/images/1. 1 times.\n"
                                "But server was requested 2 times.")


@pytest.mark.parametrize("method", ["get", "post", "patch", "delete"])
def test_has_not_raise_exception_once(server: FakeServer, method):
    requests.request(method, server.base_uri + "/musics/32")

    expect_that(server). \
        was_requested(method, "/musics/32"). \
        exactly_once(). \
        check()


@pytest.mark.parametrize("method", ["get", "post", "patch", "delete"])
def test_has_requested_raise_exception_twice(server: FakeServer, method):
    requests.request(method, server.base_uri + "/images/1")

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested(method, "/images/1"). \
            exactly_twice(). \
            check()

    assert str(error.value) == (f"Expect that server was requested with [{method.upper()}] "
                                f"http://localhost:8081/images/1. 2 times.\n"
                                "But server was requested 1 times.")


@pytest.mark.parametrize("method", ["get", "post", "patch", "delete"])
def test_has_not_requested_raise_exception_twice(server: FakeServer, method):
    requests.request(method, server.base_uri + "/images/1")
    requests.request(method, server.base_uri + "/images/1")

    expect_that(server). \
        was_requested(method, "/images/1"). \
        exactly_twice(). \
        check()


@pytest.mark.parametrize("method", ["get", "post", "patch", "delete"])
def test_has_requested_raise_exception_3_times(server: FakeServer, method):
    requests.request(method, server.base_uri + "/images/1")
    requests.request(method, server.base_uri + "/images/1")
    requests.request(method, server.base_uri + "/images/1")
    requests.request(method, server.base_uri + "/images/1")

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested(method, "/images/1"). \
            exactly_3_times(). \
            check()

    assert str(error.value) == (f"Expect that server was requested with [{method.upper()}] "
                                f"http://localhost:8081/images/1. 3 times.\n"
                                "But server was requested 4 times.")


@pytest.mark.parametrize("method", ["get", "post", "patch", "delete"])
def test_has_not_requested_raise_exception_3_times(server: FakeServer, method):
    requests.request(method, server.base_uri + "/images/1")
    requests.request(method, server.base_uri + "/images/1")
    requests.request(method, server.base_uri + "/images/1")

    expect_that(server). \
        was_requested(method, "/images/1"). \
        exactly_3_times(). \
        check()


def test_type_error_in_exactly_n_times(server: FakeServer):
    requests.get(server.base_uri + "/users")

    with pytest.raises(AttributeError) as error:
        expect_that(server). \
            was_requested("get", "/images/1"). \
            exectly_5_times()

    assert str(error.value) == "'Statistic' object has no attribute 'exectly_5_times'"


def test_drop_expectation_in_statistic_after_check(server: FakeServer):
    requests.get(server.base_uri + "/users")

    with pytest.raises(AssertionError):
        expect_that(server). \
            was_requested("get", "/users"). \
            exactly_twice(). \
            check()

    expect_that(server). \
        was_requested("get", "/users"). \
        check()


@pytest.mark.parametrize("method", ["get", "post", "patch", "delete"])
def test_has_not_requested_raise_exception(server: FakeServer, method):
    requests.request(method, server.base_uri + "/games")

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_not_requested(method, "/games"). \
            check()

    assert str(error.value) == (f"Expect that server was requested with [{method.upper()}] "
                                f"http://localhost:8081/games. 0 times.\n"
                                "But server was requested 1 times.")


@pytest.mark.parametrize("method", ["get", "post", "patch", "delete"])
def test_has_not_requested_not_raise_exception(server: FakeServer, method):
    expect_that(server). \
        was_not_requested(method, "/games"). \
        check()


def test_concrete_expectations_raise_error(server: FakeServer):
    requests.get(server.base_uri + "/photos", cookies={"token": "some_token"})

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("get", "/photos"). \
            exactly_once(). \
            for_the_first_time(). \
            with_cookies({"token": "other_token"}). \
            check()

    assert str(error.value) == ("Expect that server was requested with [GET] http://localhost:8081/photos.\n"
                                "For the 1 time: with cookies {'token': 'other_token'}.\n"
                                "But for the 1 time: cookies was {'token': 'some_token'}.")


def test_with_cookies_in_any_order(server: FakeServer):
    requests.get(server.base_uri + "/photos", cookies={"cookie1": "value1", "cookie2": "value2"})

    expect_that(server). \
        was_requested("get", "/photos"). \
        for_the_first_time(). \
        with_cookies({"cookie2": "value2", "cookie1": "value1"})


def test_concrete_expectations_not_raise_error_when_ok(server: FakeServer):
    requests.get(server.base_uri + "/photos", cookies={"token": "token", "other": "other"})

    expect_that(server). \
        was_requested("get", "/photos"). \
        for_the_first_time(). \
        with_cookies({"other": "other", "token": "token"}). \
        check()


def test_out_of_index_raise_error_second(server: FakeServer):
    requests.post(server.base_uri + "/users")

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("post", "/users"). \
            for_the_second_time()

    assert str(error.value) == ("Expect that server was requested with [POST] http://localhost:8081/users. "
                                "At least 2 times.\n"
                                "But server was requested 1 times.")


def test_out_of_index_raise_error_first(server: FakeServer):
    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("post", "/users"). \
            for_the_first_time()

    assert str(error.value) == ("Expect that server was requested with [POST] http://localhost:8081/users. "
                                "At least 1 times.\n"
                                "But server was requested 0 times.")


def test_out_of_index_raise_error_nth(server: FakeServer):
    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("post", "/users"). \
            for_the_10_time()

    assert str(error.value) == ("Expect that server was requested with [POST] http://localhost:8081/users. "
                                "At least 10 times.\n"
                                "But server was requested 0 times.")


def test_chain_number_of_times_raise_error(server: FakeServer):
    requests.get(server.base_uri + "/photos", cookies={"token": "some_token"})
    requests.get(server.base_uri + "/photos", cookies={"token": "some_token"})

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("get", "/photos"). \
            exactly_twice(). \
            for_the_first_time(). \
            with_cookies({"token": "other_token"}). \
            for_the_second_time(). \
            with_cookies({"token": "other_token_2"}). \
            check()

    assert str(error.value) == ("Expect that server was requested with [GET] http://localhost:8081/photos.\n"
                                "For the 1 time: with cookies {'token': 'other_token'}.\n"
                                "But for the 1 time: cookies was {'token': 'some_token'}.\n"
                                "For the 2 time: with cookies {'token': 'other_token_2'}.\n"
                                "But for the 2 time: cookies was {'token': 'some_token'}.")


def test_add_body_to_compare(server: FakeServer):
    requests.post(server.base_uri + "/users", data="Hello, Lord!")

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("post", "/users"). \
            exactly_once(). \
            for_the_first_time(). \
            with_body("Hello, World!"). \
            check()

    assert str(error.value) == ("Expect that server was requested with [POST] http://localhost:8081/users.\n"
                                "For the 1 time: with body 'Hello, World!'.\n"
                                "But for the 1 time: body was 'Hello, Lord!'.")


def test_with_body_not_raise_error(server: FakeServer):
    requests.patch(server.base_uri + "/sleep", data="Good night!")

    expect_that(server). \
        was_requested("patch", "/sleep"). \
        for_the_first_time(). \
        with_body("Good night!"). \
        check()


def test_exactly_nth_raise_error_immediately(server: FakeServer):
    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("post", "/users"). \
            exactly_100500_times()

    assert str(error.value) == ("Expect that server was requested with [POST] http://localhost:8081/users. "
                                "100500 times.\n"
                                "But server was requested 0 times.")


def test_with_content_type_raise_error(server: FakeServer):
    requests.post(server.base_uri + "/users", headers={"content-type": "text/plain"})

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("post", "/users"). \
            exactly_once(). \
            for_the_first_time(). \
            with_content_type("application/json"). \
            check()

    assert str(error.value) == ("Expect that server was requested with [POST] http://localhost:8081/users.\n"
                                "For the 1 time: with content type 'application/json'.\n"
                                "But for the 1 time: content type was 'text/plain'.")


def test_with_content_type_not_raise_error(server: FakeServer):
    requests.post(server.base_uri + "/users", json={"hello": "world"})

    expect_that(server). \
        was_requested("post", "/users"). \
        for_the_first_time(). \
        with_content_type("application/json")


def test_with_files_raise_error(server: FakeServer):
    requests.post(server.base_uri + "/songs", files={"song": b"power_wolf"})

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("post", "/songs"). \
            for_the_first_time(). \
            with_files({"song": b"sabaton"}). \
            check()

    assert str(error.value) == ("Expect that server was requested with [POST] http://localhost:8081/songs.\n"
                                "For the 1 time: with files {'song': b'sabaton'}.\n"
                                "But for the 1 time: files was {'song': b'power_wolf'}.")


def test_with_files_not_raise_error(server: FakeServer):
    requests.post(server.base_uri + "/songs", files={"song": b"power_wolf"})

    expect_that(server). \
        was_requested("post", "/songs"). \
        for_the_first_time(). \
        with_files({"song": b"power_wolf"}). \
        check()


def test_chain_of_different_with_errors(server: FakeServer):
    requests.patch(server.base_uri + "/users", json={"name": "new_name"})

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("patch", "/users"). \
            for_the_first_time(). \
            with_content_type("text/plain"). \
            with_body("old name"). \
            check()

    assert str(error.value) == ("Expect that server was requested with [PATCH] http://localhost:8081/users.\n"
                                "For the 1 time: with content type 'text/plain'.\n"
                                "But for the 1 time: content type was 'application/json'.\n"
                                "For the 1 time: with body 'old name'.\n"
                                "But for the 1 time: body was '{\"name\": \"new_name\"}'.")


def test_chain_of_different_with_ok(server: FakeServer):
    requests.patch(server.base_uri + "/users", json={"name": "new_name", "level": 5})

    expect_that(server). \
        was_requested("patch", "/users"). \
        for_the_first_time(). \
        with_content_type("application/json"). \
        with_body('{"name": "new_name", "level": 5}'). \
        check()


def test_chain_with_different_for_the_nth_time_error(server: FakeServer):
    requests.patch(server.base_uri + "/users", json={"name": "new_name", "level": 5})
    requests.patch(server.base_uri + "/users", json={"name": "new_name", "level": 6})
    requests.patch(server.base_uri + "/users", json={"name": "new_name", "level": 7})

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("patch", "/users"). \
            for_the_first_time(). \
            with_content_type("application/json"). \
            with_body('{"name": "new_name", "level": 6}'). \
            for_the_second_time(). \
            with_content_type("application/json"). \
            with_body('{"name": "new_name", "level": 7}'). \
            for_the_3_time(). \
            with_content_type("application/json"). \
            with_body('{"name": "new_name", "level": 8}'). \
            check()

    assert str(error.value) == ("Expect that server was requested with [PATCH] http://localhost:8081/users.\n"
                                "For the 1 time: with body '{\"name\": \"new_name\", \"level\": 6}'.\n"
                                "But for the 1 time: body was '{\"name\": \"new_name\", \"level\": 5}'.\n"
                                "For the 2 time: with body '{\"name\": \"new_name\", \"level\": 7}'.\n"
                                "But for the 2 time: body was '{\"name\": \"new_name\", \"level\": 6}'.\n"
                                "For the 3 time: with body '{\"name\": \"new_name\", \"level\": 8}'.\n"
                                "But for the 3 time: body was '{\"name\": \"new_name\", \"level\": 7}'.")


def test_chain_with_different_for_the_nth_time_ok(server: FakeServer):
    requests.patch(server.base_uri + "/users", json={"name": "new_name", "level": 6})
    requests.patch(server.base_uri + "/users", json={"name": "new_name", "level": 7})
    requests.patch(server.base_uri + "/users", json={"name": "new_name", "level": 8})

    expect_that(server). \
        was_requested("patch", "/users"). \
        for_the_first_time(). \
        with_content_type("application/json"). \
        with_body('{"name": "new_name", "level": 6}'). \
        for_the_second_time(). \
        with_content_type("application/json"). \
        with_body('{"name": "new_name", "level": 7}'). \
        for_the_3_time(). \
        with_content_type("application/json"). \
        with_body('{"name": "new_name", "level": 8}'). \
        check()


def test_raise_exception_on_with_when_concrete_time_not_specify(server: FakeServer):
    with pytest.raises(AttributeError) as error:
        expect_that(server). \
            was_requested("get", "/games/1"). \
            with_body("Hello, World!")

    assert str(error.value) == "You should specify concrete request for check with 'for_the_<any_number>_time'"


def test_with_headers_raise_error(server: FakeServer):
    requests.patch(server.base_uri + "/users", json={"name": "new_name"}, headers={"new-header": "value"})

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("patch", "/users"). \
            for_the_first_time(). \
            with_headers({"new-header": "other value"}). \
            check()

    assert str(error.value) == ("Expect that server was requested with [PATCH] http://localhost:8081/users.\n"
                                "For the 1 time: with headers contain {'NEW-HEADER': 'other value'}.\n"
                                "But for the 1 time: headers contained {'NEW-HEADER': 'value'}.")


def test_with_headers_raise_error_when_header_not_exists(server: FakeServer):
    requests.get(server.base_uri + "/hosts", headers={"other-header": "some-value"})

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("get", "/hosts"). \
            for_the_first_time(). \
            with_headers({"new-header": "other value"}). \
            check()

    assert str(error.value) == ("Expect that server was requested with [GET] http://localhost:8081/hosts.\n"
                                "For the 1 time: with headers contain {'NEW-HEADER': 'other value'}.\n"
                                "But for the 1 time: headers contained {'NEW-HEADER': <HEADER DOES NOT EXIST>}.")


def test_with_headers_not_raise_error_when_ok(server: FakeServer):
    requests.delete(server.base_uri + "/hosts/1", headers={"try-delete": "true", "other": "value"})

    expect_that(server). \
        was_requested("delete", "/hosts/1"). \
        for_the_first_time(). \
        with_headers({"other": "value", "try-delete": "true"}). \
        check()


def test_raise_exception_if_for_the_nth_time_not_specify_in_second_expectation(server: FakeServer):
    requests.delete(server.base_uri + "/hosts/1", headers={"try-delete": "true", "other": "value"})

    expect_that(server). \
        was_requested("delete", "/hosts/1"). \
        for_the_first_time(). \
        with_headers({"other": "value", "try-delete": "true"}). \
        check()

    with pytest.raises(AttributeError):
        expect_that(server). \
            was_requested("delete", "/hosts/1"). \
            with_headers({"other": "value", "try-delete": "true"})


def test_compare_unordered_json_body(server: FakeServer):
    requests.post(server.base_uri + "/songs", json={"artist": "Powerwolf", "album": "Blessed & Possessed"})

    expect_that(server). \
        was_requested("post", "/songs"). \
        for_the_first_time(). \
        with_json({"album": "Blessed & Possessed", "artist": "Powerwolf"}). \
        check()


def test_compare_unordered_json_body_raise_exception(server: FakeServer):
    requests.post(server.base_uri + "/songs", json={"artist": "Powerwolf", "album": "Blessed & Possessed"})

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("post", "/songs"). \
            for_the_first_time(). \
            with_json({"album": "Blood of the Saints", "artist": "Powerwolf"}). \
            check()

    assert str(error.value) == ('Expect that server was requested with [POST] http://localhost:8081/songs.\n'
                                'For the 1 time: with json {"album": "Blood of the Saints", "artist": "Powerwolf"}.\n'
                                'But for the 1 time: json was {"album": "Blessed & Possessed", "artist": "Powerwolf"}.')


def test_compare_with_not_incoming_json_raise_exception(server: FakeServer):
    requests.post(server.base_uri + "/songs", data="Blessed & Possessed")

    with pytest.raises(AssertionError) as error:
        expect_that(server). \
            was_requested("post", "/songs"). \
            for_the_first_time(). \
            with_json({"album": "Blood of the Saints", "artist": "Powerwolf"}). \
            check()

    assert str(error.value) == ('Expect that server was requested with [POST] http://localhost:8081/songs.\n'
                                'For the 1 time: with json {"album": "Blood of the Saints", "artist": "Powerwolf"}.\n'
                                'But for the 1 time: json was corrupted \'Blessed & Possessed\'.')
