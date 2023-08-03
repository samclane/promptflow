"""
Nodes for performing tests on the model.
"""
import code
from typing import TYPE_CHECKING, Any, Optional

from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.text_data import TextData
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class AssertNode(NodeBase):
    """
    Runs an assertion on the result of the previous node
    """

    node_color = monokai.COMMENTS

    def __init__(
        self,
        flowchart: "Flowchart",
        label: str,
        assertion: Optional[TextData] = None,
        **kwargs,
    ):
        super().__init__(flowchart, label, **kwargs)
        if assertion is None:
            assertion = TextData("Assertion", "True", self.flowchart)
        self.assertion = assertion

    def run_subclass(self, before_result: Any, state) -> str:
        assert eval(self.assertion.text, globals(), state.snapshot), "Assertion failed"
        return state.result

    def serialize(self) -> dict:
        return super().serialize() | {
            "assertion": self.assertion.serialize(),
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["assertion"]


class LoggingNode(NodeBase):
    """
    Logs user-defined string to the console.
    """

    def __init__(
        self,
        flowchart: "Flowchart",
        label: str,
        debug_str: Optional[TextData] = None,
        **kwargs,
    ):
        super().__init__(flowchart, label, **kwargs)
        if debug_str is None:
            debug_str = TextData("Debug String", "{state.result}", self.flowchart)
        self.debug_str = debug_str

    def run_subclass(self, before_result: Any, state) -> str:
        debug_str = self.debug_str.text.format(state=state)
        self.logger.info(debug_str)
        return state.result  # return the result of the previous node

    def serialize(self) -> dict:
        return super().serialize() | {
            "debug_str": self.debug_str.serialize(),
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["debug_str"]


class InterpreterNode(NodeBase):
    """
    Starts an interactive Python interpreter
    """

    def run_subclass(self, before_result: Any, state) -> str:
        code.interact(local=locals())
        return state.result
