"""
Nodes that get run time input from the user
"""
import json
from typing import Any

from promptflow.src.nodes.node_base import NodeBase


class InputNode(NodeBase):
    """
    Node that prompts the user for input
    """

    def before(self, state):
        return {"input": input()}  # todo tie this into a frontend

    def run_subclass(self, before_result, state):
        if before_result["input"] == "":
            return None
        return before_result["input"]


class FileInput(NodeBase):
    """
    Reads a file and returns its contents
    """

    filename: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = kwargs.get("filename", "")

    def run_subclass(self, before_result: Any, state) -> str:
        with open(self.filename, "r", encoding="utf-8") as f:
            return f.read()

    def serialize(self) -> dict[str, Any]:
        return super().serialize() | {"filename": self.filename}


class JSONFileInput(NodeBase):
    """
    Parses a specific input from the state.result and reads a file and returns its contents
    """

    key: str = "filename"

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.key = kwargs.get("key", "")

    def run_subclass(self, before_result: Any, state) -> str:
        data = json.loads(state.result)
        with open(data[self.key], "r", encoding="utf-8") as f:
            return f.read()

    def serialize(self) -> dict[str, Any]:
        return super().serialize() | {"key": self.key}
