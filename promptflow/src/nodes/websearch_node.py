"""
Nodes for querying the web.
"""

from abc import ABC
import os
import customtkinter
from typing import Any
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.dialogues.node_options import NodeOptions
from serpapi import GoogleSearch
from googlesearch import search


class WebSearchNode(NodeBase, ABC):
    """
    Node that makes a web search.
    """


class SerpApiNode(WebSearchNode):
    """
    Query Google using the SerpApi.
    """

    def run_subclass(
        self, before_result: Any, state, console: customtkinter.CTkTextbox
    ) -> str:
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

    def run_subclass(
        self, before_result: Any, state, console: customtkinter.CTkTextbox
    ) -> str:
        results = search(str(state.result), num_results=self.num_results, advanced=True)
        s = ""
        for r in results:
            s += r.title + "\n" + r.description + "\n" + r.url + "\n\n"
        return s

    def edit_options(self, event):
        """
        Edit the options for the node.
        """
        self.options_popup = NodeOptions(self.canvas, {"num_results": self.num_results})
        self.canvas.wait_window(self.options_popup)
        if self.options_popup.cancelled:
            return
        self.num_results = int(self.options_popup.result["num_results"])
