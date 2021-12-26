from .client import HiSockClient
from typing import Optional


class HiSockGroup:
    def __init__(
        self,
        server_conn: HiSockClient,
        name: str,
        clients: Optional[list[tuple[str, int], ...]] = None,
        cache_size: int = -1,
    ):
        # Define later-to-be-used attrs
        self.server_conn = server_conn
        self.name = name
        self.cache_size = cache_size

        if cache_size >= 0:
            # cache_size <= -1: No cache
            self.cache = []

        if clients is None:
            self.clients = []
        else:
            # List elements should be (ip, port) style
            self.clients = clients

        # Contacts server
        self.server_conn.raw_send(b"$GROUP$ " + self.name.encode())
