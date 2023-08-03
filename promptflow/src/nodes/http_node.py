"""
Interface for http requests
"""
import json
from enum import Enum
from typing import Any, Callable

import bs4
import requests

from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.state import State


class RequestType(Enum):
    """
    Types of http requests- for dropdown
    """

    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"


request_functions: dict[str, Callable[[Any], requests.Response]] = {
    RequestType.GET.value: requests.get,
    RequestType.POST.value: requests.post,
    RequestType.PUT.value: requests.put,
    RequestType.DELETE.value: requests.delete,
}


class HttpNode(NodeBase):
    """
    Makes a http request
    """

    url: str
    request_type: str

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )
        self.url = kwargs.get("url", "")
        self.request_type = kwargs.get("request_type", RequestType.GET.value)

    def run_subclass(self, before_result: Any, state) -> str:
        """
        Sends a http request
        """
        try:
            data = json.loads(state.result)
        except json.decoder.JSONDecodeError:
            return "Invalid JSON"
        response = request_functions[self.request_type](self.url, json=data)
        return response.text

    def serialize(self):
        return super().serialize() | {
            "url": self.url,
            "request_type": self.request_type,
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["url", "request_type"]


class JSONRequestNode(NodeBase):
    """
    Parses the URL out of the state.result and makes a http request
    """

    key: str = "url"
    request_type: str

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )
        self.request_type = kwargs.get("request_type", RequestType.GET.value)
        self.key = kwargs.get("key", "url")

    def run_subclass(
        self,
        before_result: Any,
        state: State,
    ) -> str:
        """
        Sends a http request
        """
        try:
            data = json.loads(state.result)
            if not data[self.key].startswith("https://"):
                data[self.key] = "https://" + data[self.key]
        except json.decoder.JSONDecodeError:
            return "Invalid JSON"
        response = request_functions[self.request_type](data[self.key], json=data)
        return response.text

    def serialize(self):
        return super().serialize() | {
            "key": self.key,
            "request_type": self.request_type,
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["key", "request_type"]


class ScrapeNode(NodeBase):
    """
    Parses the URL out of the state.result and scrapes the page
    """

    key: str = "url"

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )
        self.key = kwargs.get("key", "url")

    def run_subclass(
        self,
        before_result: Any,
        state: State,
    ) -> str:
        """
        Scrapes a page
        """
        try:
            data = json.loads(state.result)
            if not data[self.key].startswith("https://"):
                data[self.key] = "https://" + data[self.key]
        except json.decoder.JSONDecodeError:
            return "Invalid JSON"
        response = requests.get(data[self.key])
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        # return only the text and links
        text = ""
        for element in soup.find_all(
            ["p", "a"]
        ):  # Specify the relevant HTML tags to extract (e.g., 'p', 'a', etc.)
            if element.name == "a":
                link_text = element.get_text()
                link_url = element.get("href", "")
                markdown_link = f"[{link_text}]({link_url})"
                element.replace_with(
                    markdown_link
                )  # Replace the link in the HTML with the markdown link
                text += markdown_link + " "
            else:
                # get text and remove newlines
                text += element.get_text().replace("\n", " ") + " "
        # escape curly braces
        text = text.replace("{", "{{").replace("}", "}}")
        lines = [line.strip() for line in text.splitlines()]
        chunks = [phrase.strip() for line in lines for phrase in line.split("  ")]
        text = "\n".join(chunk for chunk in chunks if chunk)
        return text

    def serialize(self):
        return super().serialize() | {
            "key": self.key,
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["key"]
