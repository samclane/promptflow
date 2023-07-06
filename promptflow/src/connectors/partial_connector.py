"""A connector that is being drawn by the user"""
import logging
from typing import TYPE_CHECKING, Optional

from promptflow.src.connectors.connector import Connector
from promptflow.src.nodes.node_base import NodeBase

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class PartialConnector:
    """
    A connector that is being drawn by the user
    Animates a line from the center of the node to the mouse position
    """

    def __init__(self, flowchart: "Flowchart", node: NodeBase):
        self.flowchart = flowchart
        self.logger = logging.getLogger(__name__)
        self.node = node
        self.x = node.center_x
        self.y = node.center_y

    def update(self, event):
        """
        Move the line to the mouse position
        """

    def finish(self, event):
        """
        Create a connector if the mouse is over a node
        """

    def delete(self, _):
        """Delete the line"""

    def check_exists(self, node: NodeBase) -> bool:
        """
        Check if a connector already exists between source and given
        nodes
        """
        for connector in self.flowchart.connectors:
            if connector.node1 == self.node and connector.node2 == node:
                self.logger.debug("Connector already exists")
                return True
        return False
