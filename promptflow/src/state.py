"""
State class definition
"""

from __future__ import annotations
from typing import Any
import logging
import tiktoken
from promptflow.src.serializable import Serializable


class State(Serializable):
    """
    Holds state for flowchart flow
    Wraps a dict[str, str]
    """

    def __init__(self, **kwargs):
        self.snapshot: dict[str, str] = kwargs.get("snapshot", {})
        self.history: list[dict[str, str]] = kwargs.get("history", [])
        self.result: str = kwargs.get("result", "")
        self.data: dict[str, Any] = kwargs.get("data", {})
        self.logger = logging.getLogger(__name__)

    def reset(self) -> None:
        """
        Reset state to empty
        """
        self.snapshot = {}
        self.history = []
        self.result = ""
        self.data = {}
        self.logger.debug("State reset")

    def __or__(self, __t: dict | State) -> "State":
        if isinstance(__t, dict):
            self.snapshot.update(__t)
        elif isinstance(__t, State):
            self.snapshot.update(__t.snapshot)
        return self

    def copy(self) -> "State":
        """
        Create a new State object with a copy of the snapshot and history
        """
        self.logger.debug("State copied")
        return State(
            snapshot=self.snapshot.copy(),
            history=self.history.copy(),
            result=self.result,
            data=self.data.copy(),
        )

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "State":
        return cls(**data)

    def serialize(self) -> dict[str, Any]:
        return {
            "snapshot": self.snapshot,
            "history": self.history,
            "result": self.result,
            "data": self.data,
        }

    def __getitem__(self, key: str) -> str:
        """
        Makes access in f-strings easy
        """
        return self.snapshot.get(key, "")

    @property
    def token_count(self) -> int:
        """
        Get token count of history + result
        """
        encoding = tiktoken.get_encoding("cl100k_base")  # assume gpt3/4
        count = 0
        for item in self.history:
            count += len(encoding.encode(item["content"]))
        count += len(encoding.encode(self.result))
        return count
