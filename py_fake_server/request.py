from typing import Optional, Dict

import falcon


class Request:
    def __init__(self, request: falcon.Request, request_number: int):
        self.cookies: Optional[Dict[str, str]] = request.cookies
        self.body: Optional[bytes] = request.bounded_stream.read()
        self.content_type: Optional[str] = request.content_type
        self.files: Optional[Dict[str, bytes]] = self._get_files(request)
        self.headers: Optional[Dict[str, str]] = request.headers
        self.query_params: Optional[Dict[str, str]] = request.params
        self.number = request_number

    @staticmethod
    def _get_files(request: falcon.Request) -> Optional[Dict[str, bytes]]:
        files = {
            param_name: param_value.file.read()
            for param_name, param_value in request.params.items()
            if hasattr(param_value, "file")
        }

        return files if files else None
