"""
This module contains the Connector class, which represents a connection
between two nodes in the flowchart.
"""
import math
import logging
import sqlite3
import uuid
from typing import Optional, Tuple

from promptflow.src.nodes.start_node import StartNode
from promptflow.src.serializable import Serializable
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.text_data import TextData
from promptflow.src.themes import monokai

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
        node1: NodeBase,
        node2: NodeBase,
        condition: Optional[TextData | dict] = None,
    ):
        self.node1 = node1
        self.node2 = node2
        self.id = str(uuid.uuid1())
        self.flowchart = node1.flowchart
        node1.output_connectors.append(self)
        node2.input_connectors.append(self)
        self.logger = logging.getLogger(__name__)
        # each connector has a branching condition
        if not condition:
            condition = TextData(
                DEFAULT_COND_NAME, DEFAULT_COND_TEMPLATE, self.flowchart
            )
        if isinstance(condition, dict):
            condition = TextData.deserialize(condition, self.flowchart)
        if condition.text == "":
            condition.text = DEFAULT_COND_TEMPLATE
        self.condition: TextData = condition
        self.condition_label: Optional[int] = None

    @property
    def label(self) -> str:
        return self.condition.label

    @classmethod
    def deserialize(cls, node1: NodeBase, node2: NodeBase, condition: TextData):
        return cls(node1, node2, condition)

    def serialize(self):
        return {
            "node1": self.node1.id,
            "node2": self.node2.id,
            "condition": self.condition.serialize(),
        }

    def delete(self, *args):
        """
        Remove the connector from the flowchart, both from the canvas and from the flowchart's list of connectors.
        """
        if self in self.node1.flowchart.connectors:
            self.node1.flowchart.connectors.remove(self)
        self.node1.output_connectors.remove(self)
        self.node2.input_connectors.remove(self)

    def select(self, *args):
        """
        Select the connector.
        """
        self.flowchart.selected_element = self

    def detect_cycle(self) -> bool:
        """
        Check if the node connects to itself or to a child of itself
        """
        if self.node1 == self.node2:
            return True
        if self.node1 in self.node2.get_children():
            return True
        return False

    def save_to_db(self):
        conn = sqlite3.connect("flowcharts.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO branches VALUES (?, ?, ?, ?, ?)",
            (
                self.id,
                self.node1.id,
                self.condition,
                self.condition_label,
                self.node2.id,
            ),
        )
        conn.commit()
        conn.close()


def is_condition_default(condition: TextData) -> bool:
    """
    Check if a condition is the default condition.
    """
    return (
        condition.label == DEFAULT_COND_NAME and condition.text == DEFAULT_COND_TEMPLATE
    )
