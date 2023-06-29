"""
Special node that prompts the user for input
Also signals the start of the flowchart
"""
from typing import TYPE_CHECKING, Any

from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class StartNode(NodeBase):
    """
    First node in the flowchart
    """

    node_color = monokai.BLUE

    def __init__(
        self,
        flowchart: "Flowchart",
        center_x: float,
        center_y: float,
        label: str,
        **kwargs,
    ):
        # make sure there is only one start node
        for node in flowchart.nodes:
            if isinstance(node, StartNode):
                raise ValueError("Only one start node is allowed")

        super().__init__(flowchart, center_x, center_y, label, **kwargs)

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

    def __init__(
        self,
        flowchart: "Flowchart",
        center_x: float,
        center_y: float,
        label: str,
        **kwargs,
    ):
        # make sure there is only one init node
        for node in flowchart.nodes:
            if isinstance(node, InitNode):
                raise ValueError("Only one init node is allowed")

        super().__init__(flowchart, center_x, center_y, label, **kwargs)
        self.run_once = False

    def run_subclass(self, before_result: Any, state) -> str | None:
        if not self.run_once:
            self.run_once = True
            return ""
        else:
            return None
