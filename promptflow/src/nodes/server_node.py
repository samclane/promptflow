"""
Hosts a simple HTTP server that can be used as Input node.
"""
import http.server
from typing import Any

from promptflow.src.nodes.node_base import NodeBase


class Handler(http.server.BaseHTTPRequestHandler):
    """
    Override the default HTTP request handler to allow POST requests.
    """

    def do_POST(self):
        self.send_response(200)
        self.end_headers()

        # get data from request
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        self.server.data = post_data.decode("utf-8")


class ServerInputNode(NodeBase):
    """
    Blocking node that waits for a POST request to the specified port.
    """

    host: str = ""
    port: str = "8000"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = kwargs.get("host", "")
        self.port = kwargs.get("port", "8000")

    def run_subclass(self, before_result: Any, state) -> str:
        with http.server.HTTPServer((self.host, int(self.port)), Handler) as httpd:
            httpd.handle_request()
            return httpd.data

    def serialize(self) -> dict[str, Any]:
        return super().serialize() | {"host": self.host, "port": self.port}

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["host", "port"]
