"""
This module contains the Connector class, which represents a connection
between two nodes in the flowchart.
"""
import logging
from typing import Optional

from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.serializable import Serializable
from promptflow.src.text_data import TextData

DEFAULT_COND_TEMPLATE = """def main(state):
\treturn True
"""

DEFAULT_COND_NAME = "Untitled.py"


class Connector(Serializable):
    """
    A connection between two nodes in the flowchart.
    """

    def __init__(
        self,
        prev: NodeBase,
        next: NodeBase,
        condition: Optional[TextData | dict] = None,
        uid: Optional[str] = None,
    ):
        self.prev = prev
        self.next = next
        self.uid = uid
        if self.uid is None:
            raise ValueError("uid must be specified")
        self.flowchart = prev.flowchart
        prev.output_connectors.append(self)
        next.input_connectors.append(self)
        self.logger = logging.getLogger(__name__)
        # each connector has a branching condition
        if not condition:
            condition = TextData(
                DEFAULT_COND_NAME, DEFAULT_COND_TEMPLATE, self.flowchart
            )
        if isinstance(condition, dict):
            condition = TextData.deserialize(condition, self.flowchart)
        elif isinstance(condition, str):
            condition = TextData("Untitled", condition, self.flowchart)
        if condition.text == "":
            condition.text = DEFAULT_COND_TEMPLATE
        self.condition: TextData = condition
        self.condition_label: Optional[str] = (
            None if is_condition_default(condition) else condition.label
        )

    @property
    def label(self) -> str:
        return self.condition.label

    @classmethod
    def deserialize(cls, prev: NodeBase, next: NodeBase, condition: TextData, uid: str):
        return cls(prev, next, condition, uid)

    def serialize(self):
        return {
            "uid": self.uid,
            "prev": self.prev.uid,
            "next": self.next.uid,
            "conditional": self.condition.text,
            "label": self.condition.label,
            "graph_id": self.flowchart.uid,
        }

    def delete(self, *args):
        """
        Remove the connector from the flowchart, both from the canvas and from the flowchart's list of connectors.
        """
        if self in self.prev.flowchart.connectors:
            self.prev.flowchart.connectors.remove(self)
        self.prev.output_connectors.remove(self)
        self.next.input_connectors.remove(self)

    def select(self, *args):
        """
        Select the connector.
        """
        self.flowchart.selected_element = self

    def detect_cycle(self) -> bool:
        """
        Check if the node connects to itself or to a child of itself
        """
        if self.prev == self.next:
            return True
        if self.prev in self.next.get_children():
            return True
        return False


def is_condition_default(condition: TextData) -> bool:
    """
    Check if a condition is the default condition.
    """
    return (
        condition.label == DEFAULT_COND_NAME and condition.text == DEFAULT_COND_TEMPLATE
    )
