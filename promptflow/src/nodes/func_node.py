"""
Node to run arbitrary Python code.
"""

from typing import Any, TYPE_CHECKING, Optional
from abc import ABC

from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.state import State
from promptflow.src.text_data import TextData
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


DEFAULT_FUNC_TEMPLATE = """def main(state):
\treturn True
"""


class FuncNode(NodeBase, ABC):
    """
    Run arbitrary Python code.
    """

    node_color = monokai.YELLOW
    func: Optional[TextData] = None

    def __init__(
        self,
        flowchart: "Flowchart",
        center_x: float,
        center_y: float,
        label: str,
        func: Optional[TextData] = None,
        **kwargs,
    ):
        super().__init__(flowchart, center_x, center_y, label, **kwargs)
        if not self.func:
            self.func = TextData("func.py", DEFAULT_FUNC_TEMPLATE, flowchart)
        if isinstance(func, dict):
            self.func = TextData.deserialize(func, self.flowchart)
        if self.func.text == "":
            self.func.text = DEFAULT_FUNC_TEMPLATE
        # convert function to string
        self.functext = self.func.label

    def run_subclass(self, before_result: Any, state) -> str:
        """
        Evaluate the Python function and return the result.
        """
        loc = state.copy() | {"result": None}
        try:
            exec(self.func.text, dict(globals()), loc.snapshot)
        except Exception as node_exception:
            raise RuntimeError(
                f"Error in function: {node_exception}"
            ) from node_exception
        if "main" not in loc.snapshot:
            raise NameError("Function must have a main() function")
        # todo make this less hacky
        result = loc.snapshot["main"](state)  # type: ignore
        return result

    def serialize(self):
        return super().serialize() | {
            "func": {
                "label": self.func.label,
                "text": self.func.text,
            }
        }

    @classmethod
    def deserialize(cls, flowchart: "Flowchart", data: dict):
        node = super().deserialize(flowchart, data)
        node.func = TextData(data["func"]["label"], data["func"]["text"], flowchart)
        return node

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["func"] = self.func.serialize() if self.func else None
        base_options["editor"] = "python"
        return base_options
