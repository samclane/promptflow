"""
Nodes that output data to the user, such as text or files
"""

import json
from typing import Any

from promptflow.src.nodes.node_base import NodeBase


class FileOutput(NodeBase):
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

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["filename"] = self.filename
        base_options["options"]["mode"] = self.mode
        return base_options


class JSONFileOutput(NodeBase):
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

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["filename_key"] = self.filename_key
        base_options["options"]["data_key"] = self.data_key
        base_options["options"]["mode"] = self.mode
        return base_options
