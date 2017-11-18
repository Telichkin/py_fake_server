# py_fake_server
[![Build Status](https://travis-ci.org/Telichkin/py_fake_server.svg?branch=master)](https://travis-ci.org/Telichkin/py_fake_server)
[![codecov](https://codecov.io/gh/Telichkin/py_fake_server/branch/master/graph/badge.svg)](https://codecov.io/gh/Telichkin/py_fake_server)
[![Python versions](https://img.shields.io/pypi/pyversions/py_fake_server.svg)](https://pypi.python.org/pypi/py_fake_server)

**py_fake_server** is a small Python library that gives you the ability to create high-level tests (functional tests) for your services/microservices without having to connect to real external http-services. It provides declarative API for both creating the server and for checking the expectation.

## Table of contents:
* [Install](#install)
* [Getting Started](#getting-started)
* [A more complex example](#a-more-complex-example)
* [Documentation by example](#documentation-by-example)
    * [Start server](#start-server)
    * [Stop server](#stop-server)
    * [Create endpoint](#create-endpoint)
    * [Clear created endpoints](#clear-created-endpoints)
    * [Check expectations](#check-expectations)

## Install
`pip3 install py_fake_server`


## Getting Started

Here is a simple example showing how to create a dummy test with **py_fake_server**.

```python
# dummy_test.py

import requests
from py_fake_server import FakeServer


def test_simple_example():
    server = FakeServer(host="localhost", port=8081)
    server.start()
    server.on_("get", "/hello"). \
        response(status=200, body="Hello, World!", content_type="text/plain")
    
    response = requests.get(server.base_uri + "/hello")
    
    assert server.was_requested("get", "/hello"). \
        exactly_once().check()
        
```


## A more complex example

The one of the best example to show necessary and simplicity of this library is testing the API-Gateway service in isolation. Imagine, that our API-Gateway should check a user authentication in an auth microservice before update the user information in a portfolio microservice. 
```
                       ┌───────────────┐ POST /auth             ┌──────────────┐
                       |               | <--------------------> | Auth-service |
PATCH /portfolios/34   |               |              HTTP 200  └──────────────┘
---------------------> |  API-Gateway  |
             HTTP 204  |               | PATCH /portfolios/34   ┌───────────────────┐           
                       |               | <--------------------> | Portfolio-service |
                       └───────────────┘              HTTP 204  └───────────────────┘
```


We don't want to up and run both auth and portfolio microservices, but we can use `FakeServer` instances instead.

```
                       ┌───────────────┐ POST /auth             ┌─────────────────────┐
                       |               | <--------------------> | FakeServer instance |
PATCH /portfolios/34   |               |              HTTP 200  └─────────────────────┘
---------------------> |  API-Gateway  |
             HTTP 204  |               | PATCH /portfolios/34   ┌─────────────────────┐           
                       |               | <--------------------> | FakeServer instance |
                       └───────────────┘              HTTP 204  └─────────────────────┘
```

Here is how it'll look in the code, using [pytest](https://github.com/pytest-dev/pytest) as a testing framework.

```python
# api_gateway_test.py

import pytest
import requests
from py_fake_server import FakeServer

API_GATEWAY_BASE_URI = "http://localhost:8080"


@pytest.fixture(scope="session")
def auth_server():
    server = FakeServer(host="localhost", port=8081)
    server.start()
    yield server
    server.stop()


@pytest.fixture(scope="session")
def portfolio_server():
    server = FakeServer(host="localhost", port=8082)
    server.start()
    yield server
    server.stop()


@pytest.fixture(scope="function", autouse=True)
def servers_cleanup(auth_server, portfolio_server):
    auth_server.clear()
    portfolio_server.clear()
    yield
    auth_server.clear()
    portfolio_server.clear()


def test_patch_portfolio_description(auth_server: FakeServer, portfolio_server: FakeServer):
    auth_server.on_("post", "/auth"). \
        response(status=200, json={"user_id": "34"})

    portfolio_server.on_("patch", "/portfolios/34"). \
        response(status=204)

    requests.patch(API_GATEWAY_BASE_URI + "/users/34/portfolio",
                   json={"description": "Brand new Description"},
                   cookies={"token": "auth-token-with-encrypted-user-id-34"})

    assert auth_server.was_requested("post", "/auth"). \
        exactly_once(). \
        for_the_first_time(). \
        with_cookies({"token": "auth-token-with-encrypted-user-id-34"}).check()

    assert portfolio_server.was_requested("patch", "/portfolios/34"). \
        exactly_once(). \
        for_the_first_time(). \
        with_query_params({"requested_user_id": "34"}). \
        with_json({"description": "Brand new Description"}). \
        with_content_type("application/json").check()
```


## Documentation by example

### Start server
```python
server = FakeServer(host="localhost", port=8081)
server.start()
```

### Stop server
```python
server = FakeServer(host="localhost", port=8081)
server.start()
server.stop()
```

### Create endpoint
Simple endpoint:

```python

server.on_("get", "/some/path"). \
    response(status=200, body="Hello, World!", content_type="text/plain",
             headers={"Header Name": "Header Value"}, cookies={"Cookie Name": "Cookie Value"})
```

Specify number of responses:
```python

server.on_("post", "/some/path/1"). \
    response(status=204).once()

server.on_("post", "/some/path/2"). \
    response(status=204).twice()

server.on_("post", "/some/path/3"). \
    response(status=204)._3_times()

server.on_("post", "/some/path/100"). \
    response(status=204)._100_times()
```

When requests endpoint more times than was specified:
```python
import requests

server.on_("post", "/some/path/1"). \
    response(status=204).once()
 
response_1 = requests.post(server.base_uri + "/some/path/1")
response_2 = requests.post(server.base_uri + "/some/path/1")

response_1.status_code  # -> 204
response_2.status_code  # -> 500
response_2.text         # -> Server has not responses for [POST] http://localhost:8081/some/path/1
```

Specify chain of responses:
```python
server.on_("post", "/some/path/1"). \
    response(status=204).once(). \
    then(). \
    response(status=401).once(). \
    then(). \
    response(status=204)
```

### Clear created endpoints 
```python
server.clear()
```

### Check expectations
Three interchangeable ways:
```python
from py_fake_server import expect_that

# With an explicit call to the method "check()"
assert server.was_requested("get", "/some/path").check()
expect_that(server).was_requested("get", "/some/path").check()

# Without a call to the method "check()"
expect_that(server.was_requested("get", "/some/path"))
```

Expected number of requests:
```python
assert server.was_requested("post", "/some/path/1"). \
    exactly_once().check()

assert server.was_requested("post", "/some/path/2"). \
    exactly_twice().check()
    
assert server.was_requested("post", "/some/path/3"). \
    exactly_3_times().check()

assert server.was_requested("post", "/some/path/100"). \
    exactly_100_times().check()
```

Endpoint is never called:
```python
assert server.was_not_requested("post", "/never/called").check()
```

Specify the number of the check:
```python
assert server.was_requested("patch", "/some/path/1"). \
    for_the_first_time(). \
    with_body("The first time body").check()

assert server.was_requested("patch", "/some/path/2"). \
    for_the_second_time(). \
    with_body("The second time body").check()

assert server.was_requested("patch", "/some/path/3"). \
    for_the_3_time(). \
    with_body("The third time body").check()

assert server.was_requested("patch", "/some/path/100"). \
    for_the_100_time(). \
    with_body("The 100th time body").check()

# Mix all together!
assert server.was_requested("patch", "/some/path"). \
    exactly_101_times(). \
    for_the_first_time(). \
    with_body("The first time body"). \
    for_the_second_time(). \
    with_body("The second time body"). \
    for_the_3_time(). \
    with_body("The third time body"). \
    for_the_100_time(). \
    with_body("The 100th time body").check()
```

Different types of the check:
```python
assert server.was_requested("post", "some/path"). \
    exactly_5_times().\ 
    for_the_second_time(). \
    with_body("Expected string body"). \
    with_json({"Expected": "dictionary"}). \
    with_files({"Expected": b"file"}). \
    with_cookies({"Expected": "Cookie"}). \
    with_headers({"Containts": "This header"}). \
    with_content_type("String/Content-Type"). \
    with_query_params({"Expected": "Query parameter"}). \
    check()
```


## License
MIT License

Copyright (c) 2017 Roman Telichkin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
