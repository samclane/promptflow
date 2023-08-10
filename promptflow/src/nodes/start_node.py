"""
Special node that prompts the user for input
Also signals the start of the flowchart
"""
from typing import TYPE_CHECKING, Any

from promptflow.src.nodes.node_base import FlowchartJSTypes, NodeBase, NxNodeShape
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class StartNode(NodeBase):
    """
    First node in the flowchart
    """

    node_color = monokai.BLUE
    nx_shape = NxNodeShape.CIRCLE
    js_shape = FlowchartJSTypes.start

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # make sure there is only one start node
        for node in self.flowchart.nodes:
            if isinstance(node, StartNode):
                raise ValueError("Only one start node is allowed")

    @classmethod
    def deserialize(cls, flowchart: "Flowchart", data: dict):
        return cls(flowchart, **data)

    def run_subclass(self, before_result: Any, state) -> str:
        return ""


class InitNode(NodeBase):
    """
    Initialization node that is only run once at the beginning of the flowchart
    """

    node_color = monokai.ORANGE
    nx_shape = NxNodeShape.CIRCLE
    js_shape = FlowchartJSTypes.start

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # make sure there is only one init node
        for node in self.flowchart.nodes:
            if isinstance(node, InitNode):
                raise ValueError("Only one init node is allowed")

        self.run_once = False

    def run_subclass(self, before_result: Any, state) -> str | None:
        if not self.run_once:
            self.run_once = True
            return ""
        else:
            return None
