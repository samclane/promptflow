"""
Nodes that get run time input from the user
"""
from abc import ABC
import json
from typing import Any

from promptflow.src.nodes.node_base import FlowchartJSTypes, NodeBase
from promptflow.src.themes import monokai


class InputNode(NodeBase, ABC):
    js_shape = FlowchartJSTypes.inputoutput
    color = monokai.YELLOW


class UserInputNode(InputNode):
    """
    Node that prompts the user for input
    """

    def before(self, state):
        return {"input": ""}

    def run_subclass(self, before_result, state):
        if before_result["input"] == "":
            return None
        return before_result["input"]


class FileInput(InputNode):
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

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["filename"]


class JSONFileInput(InputNode):
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

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["key"]
