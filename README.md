# py_fake_server
[![Build Status](https://travis-ci.org/Telichkin/py_fake_server.svg?branch=master)](https://travis-ci.org/Telichkin/py_fake_server)
[![Python versions](https://img.shields.io/pypi/pyversions/py_fake_server.svg)](https://pypi.python.org/pypi/py_fake_server)

py_fake_server helps you create fake servers with pleasure. It provides
declarative API both for server creation and for checking expectation.
Let's look at some examples below!

- First of all, you should create server and start it:
```python
# test.py

from py_fake_server import FakeServer

server = FakeServer(host="localhost", port=8081)
server.start()
```
Server started in the background and you can continue work in the
same process (thread).

- After that you can add some endpoints:
```python
# test.py
# previous code

server. \
    on_("post", "/users"). \
    response(status=200, body="Hello, World!", content_type="text/plain"). \
    once(). \
    then(). \
    response(status=200, body='{"message": "Goodbye, World!"}',
             content_type="application/json"). \
    once()
```

- Now you can access your server:
```python
# test.py
# previous code

import requests

response_1 = requests.post(server.base_uri + "/users", json={"test": "value"})
assert response_1.status_code == 200
assert response_1.text == "Hello, World!"
assert response_1.headers["content-type"] == "text/plain"

response_2 = requests.post(server.base_uri + "/users", json={"test": "value2"})
assert response_2.status_code == 200
assert response_2.json() == {"message": "Goodbye, World!"}
assert response_2.headers["content-type"] == "application/json"

response_3 = requests.post(server.base_uri + "/users", json={"test": "value3"})
assert response_3.status_code == 500
assert response_3.text == "Server has not responses for [POST] http://localhost:8081/users"

```

- And you can check some expectation on created endpoint:
```python
# test.py
# previous code

from py_fake_server import expect_that

expect_that(server). \
    was_requested("post", "/users"). \
    exactly_3_times(). \
    for_the_first_time() .\
    with_json({"test": "value"}). \
    for_the_second_time(). \
    with_json({"test": "value2"}). \
    for_the_3_time(). \
    with_json({"test": "value3"}). \
    check()
```

For more examples see documentation below [in progress]

## Install
```pip3 install py_fake_server```

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
