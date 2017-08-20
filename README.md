# py_fake_server

## Install
```pip install py_fake_server```

## Usage
```python
import requests
from py_fake_server import FakeServer, expect_that

server = FakeServer(host="localhost", port=8081)
server.start()

server.\
    on_("post", "/data").\
    response(status=200, body="text", content_type="text/plain")

response = requests.post(server.base_uri + "/data", json={"name": "Fake!"})
assert response.status_code == 200
assert response.text == "text"

expect_that(server). \
  was_requested("post", "/data"). \
  exactly_once(). \
  for_the_first_time().\
  with_body('{"name": "Fake!"}'). \
  with_content_type("application/json"). \
  check()

```
