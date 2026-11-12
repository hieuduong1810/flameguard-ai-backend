class Phase4Error(Exception):
    def __init__(self, code: str, status: int = 503, fields=(), supported=()):
        super().__init__(code)
        self.code, self.status = code, status
        self.fields, self.supported = list(fields), list(supported)


def unknown_context():
    return {"collectionId": "unknown", "origin": "unknown", "reviewState": "unknown", "caveats": []}
