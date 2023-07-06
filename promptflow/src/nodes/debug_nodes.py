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
        center_x: float,
        center_y: float,
        label: str,
        assertion: Optional[TextData] = None,
        **kwargs,
    ):
        super().__init__(flowchart, center_x, center_y, label, **kwargs)
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

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["assertion"] = self.assertion.serialize()
        return base_options


class LoggingNode(NodeBase):
    """
    Logs user-defined string to the console.
    """

    def __init__(
        self,
        flowchart: "Flowchart",
        center_x: float,
        center_y: float,
        label: str,
        debug_str: Optional[TextData] = None,
        **kwargs,
    ):
        super().__init__(flowchart, center_x, center_y, label, **kwargs)
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

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["debug_str"] = self.debug_str.serialize()
        return base_options


class InterpreterNode(NodeBase):
    """
    Starts an interactive Python interpreter
    """

    def run_subclass(self, before_result: Any, state) -> str:
        code.interact(local=locals())
        return state.result
