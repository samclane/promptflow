"""
Initialize environmental variables using .env
"""
import os
from typing import Any

from dotenv import load_dotenv

from promptflow.src.nodes.node_base import NodeBase


class EnvNode(NodeBase):
    """
    Loads environmental variables from a .env file
    """

    filename: str = ".env"

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.filename = kwargs.get("filename", ".env")

    def run_subclass(self, before_result: Any, state) -> str:
        load_dotenv(self.filename)
        return state.result

    def serialize(self):
        return super().serialize() | {
            "filename": self.filename,
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["filename"]


class ManualEnvNode(NodeBase):
    """
    Manually set an environmental variable
    """

    key: str = ""
    val: str = ""

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.key = kwargs.get("key", "")
        self.val = kwargs.get("val", "")

    def run_subclass(self, before_result: Any, state) -> str:
        os.environ[self.key] = self.val
        return state.result

    def serialize(self):
        return super().serialize() | {
            "key": self.key,
            "val": self.val,
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["key", "val"]
