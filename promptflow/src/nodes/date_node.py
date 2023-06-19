"""
Convenience node for injecting date into state
"""
import datetime
from typing import TYPE_CHECKING, Any
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class DateNode(NodeBase):
    """
    Injects date into state
    """

    node_color = monokai.PINK

    def __init__(
        self,
        flowchart: "Flowchart",
        center_x: float,
        center_y: float,
        label: str,
        **kwargs,
    ):
        super().__init__(
            flowchart,
            center_x,
            center_y,
            label,
            **kwargs,
        )
        self.options_popup = None
        self.datetime_format = "%m/%d/%Y, %H:%M:%S"

    def run_subclass(self, before_result: Any, state) -> str:
        """
        Injects date into state
        """
        date_time = datetime.datetime.now().strftime(self.datetime_format)
        self.logger.info("Date node %s has state %s", self.label, state)
        return date_time

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["datetime_format"] = self.datetime_format
        return base_options
