from typing import List, Tuple, Dict, Optional, Union
from urllib.parse import urlencode
from .utils import UtilsMonitoring
import logging

logger = logging.getLogger(__name__)


class Route:
    @UtilsMonitoring.io_display(input=True, output=False, level=logging.DEBUG)
    def __init__(self, method: str, base_url: str, uri: str):
        self.method = method.lower()
        self.url = base_url + uri.rstrip("/")
        self._route_as_tuple = (self.method, self.url)

    def __hash__(self):
        return hash(self._route_as_tuple)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __str__(self):
        return f"<{Route.__name__} | {self.method} {self.url}>"