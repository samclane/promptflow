"""
Nodes for querying the web.
"""

import os
from abc import ABC
from typing import Any

from googlesearch import search
from serpapi import GoogleSearch

from promptflow.src.nodes.node_base import NodeBase


class WebSearchNode(NodeBase, ABC):
    """
    Node that makes a web search.
    """


class SerpApiNode(WebSearchNode):
    """
    Query Google using the SerpApi.
    """

    def run_subclass(self, before_result: Any, state) -> str:
        searchParams = {
            "engine": "google",
            "q": str(state.result),
            "location": "Austin, Texas, United States",
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "api_key": os.environ["SERP_API_KEY"],
        }
        search = GoogleSearch(searchParams)
        results = search.get_dict().get("organic_results", [])
        return str(results)


class GoogleSearchNode(WebSearchNode):
    """
    Query Google using the googlesearch library.
    """

    num_results = 10

    def __init__(self, *args, num_results: int = 10, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_results = num_results

    def run_subclass(self, before_result: Any, state) -> str:
        results = search(str(state.result), num_results=self.num_results, advanced=True)
        s = ""
        for r in results:
            s += r.title + "\n" + r.description + "\n" + r.url + "\n\n"
        return s

    def serialize(self):
        return super().serialize() | {"num_results": self.num_results}

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["num_results"] = self.num_results
        return base_options
