class Route:
    def __init__(self, method: str, base_url: str, uri: str):
        self.method = method.lower()
        self.url = base_url + uri.rstrip("/")
        self._route_as_tuple = (self.method, self.url)

    def __hash__(self):
        return hash(self._route_as_tuple)

    def __eq__(self, other):
        return hash(self) == hash(other)
