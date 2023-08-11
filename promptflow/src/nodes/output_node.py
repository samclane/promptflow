"""
Nodes that output data to the user, such as text or files
"""

import json
from typing import Any

from promptflow.src.nodes.node_base import FlowchartJSTypes, NodeBase
from promptflow.src.themes import monokai


class OutputNode(NodeBase):
    js_shape = FlowchartJSTypes.inputoutput
    color = monokai.BLUE


class FileOutput(OutputNode):
    """
    Outputs data to a file
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = kwargs.get("filename", "")
        self.mode = kwargs.get("mode", "w")

    def run_subclass(self, before_result: Any, state):
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(state.result)
        return state.result

    def serialize(self) -> dict[str, Any]:
        return super().serialize() | {
            "filename": self.filename,
            "mode": self.mode,
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["filename", "mode"]


class JSONFileOutput(OutputNode):
    """
    Outputs data to a file location parsed from the state.result
    """

    filename_key: str = "filename"
    data_key: str = "data"
    mode: str = "w"

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.filename_key = kwargs.get("filename_key", "")
        self.data_key = kwargs.get("data_key", "")
        self.mode = kwargs.get("mode", "w")

    def run_subclass(self, before_result: Any, state):
        data = json.loads(state.result)
        filename = data[self.filename_key]
        with open(filename, self.mode, encoding="utf-8") as f:
            f.write(data[self.data_key])
        return state.result

    def serialize(self) -> dict[str, Any]:
        return super().serialize() | {
            "filename_key": self.filename_key,
            "data_key": self.data_key,
            "mode": self.mode,
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["filename_key", "data_key", "mode"]
