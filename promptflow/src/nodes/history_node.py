"""
Manages writing history to state
"""
from abc import ABC
from typing import TYPE_CHECKING, Any, Optional

import tiktoken

from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.state import State
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class HistoryNode(NodeBase):
    """
    Injects history into state
    """

    node_color = monokai.PINK
    role_var: Optional[str] = None

    def run_subclass(self, before_result: Any, state: State) -> str:
        """
        Injects date into state
        """
        state.history.append({"role": self.role_var, "content": state.result})
        return state.result

    def serialize(self):
        return super().serialize() | {
            "role": self.role_var,
        }

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["role"] = self.role_var
        return base_options


class ManualHistoryNode(NodeBase):
    """
    Allows the user to specify a long history manually
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )
        self.manual_history = kwargs.pop("manual_history", [])

    def run_subclass(self, before_result: Any, state) -> str:
        state.history.extend(self.manual_history)
        return state.result

    def serialize(self):
        return super().serialize() | {"manual_history": self.manual_history}

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        # todo make this a better serialization
        base_options["options"]["manual_history"] = self.manual_history
        return base_options


class HistoryWindow(NodeBase, ABC):
    """
    Stores messages in a list
    """

    node_color = monokai.BLUE

    def apply_window(self, state: State) -> list[dict[str, str]]:
        """
        Update state history
        """
        state.history = state.history
        return state.history

    def run_subclass(self, before_result: Any, state) -> str:
        history_string = "\n".join(
            [
                *[
                    f"{message['role']}: {message['content']}"
                    for message in self.apply_window(state)
                ],
            ]
        )
        return history_string


class WindowedHistoryNode(HistoryWindow):
    """
    Like MemoryNode, but only returns the last n messages
    """

    def __init__(
        self,
        flowchart: "Flowchart",
        label: str,
        window: int = 100,
        **kwargs,
    ):
        super().__init__(
            flowchart,
            label,
            **kwargs,
        )
        self.window = window

    def apply_window(self, state):
        # find where to start the window
        total_tokens = 0
        i = 0
        enc = tiktoken.get_encoding("cl100k_base")
        for i, message in enumerate(reversed(state.history)):
            encoded = enc.encode(message["content"])
            if total_tokens + len(encoded) > self.window:
                break
            total_tokens += len(encoded)
        state.history = state.history[-i:]

        return state.history

    def serialize(self):
        return super().serialize() | {"window": self.window}

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["window"] = self.window
        return base_options


class DynamicWindowedHistoryNode(HistoryWindow):
    """
    Given a string, will return the last n messages until the string is found
    """

    def __init__(
        self,
        flowchart: "Flowchart",
        label: str,
        target: str = "",
        **kwargs,
    ):
        super().__init__(
            flowchart,
            label,
            **kwargs,
        )
        self.target = target

    def apply_window(self, state: State) -> list[dict[str, str]]:
        """
        Update state history
        """
        history = state.history
        for i, message in enumerate(history):
            if eval(self.target, {}, message):
                history = history[i:]
                break
        return history

    def serialize(self):
        return super().serialize() | {"target": self.target}

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["target"] = self.target
        return base_options
