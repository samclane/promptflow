"""
Base class for all nodes
"""
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any

from promptflow.src.mermaid_converter import MermaidNodeShape
from promptflow.src.serializable import Serializable
from promptflow.src.state import State
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.connectors.connector import Connector
    from promptflow.src.flowchart import Flowchart


class NxNodeShape(Enum):
    """Options for the shape of the node"""

    SQUARE = "s"
    CIRCLE = "o"
    UP_ARROW = "^"
    RIGHT_ARROW = ">"
    DOWN_ARROW = "v"
    LEFT_ARROW = "<"
    DIAMOND = "d"
    PENTAGON = "p"
    HEXAGON = "h"
    OCTAGON = "8"


class FlowchartJSTypes(Enum):
    start = "start"
    end = "end"
    operation = "operation"
    inputoutput = "inputoutput"
    subroutine = "subroutine"
    condition = "condition"
    parallel = "parallel"


class NodeBase(Serializable, ABC):
    """
    Represents a node in the flowchart, which could be a prompt, an llm, traditional code, etc.
    """

    color = monokai.WHITE
    nx_shape = NxNodeShape.SQUARE
    js_shape = FlowchartJSTypes.operation
    mermaid_shape = MermaidNodeShape.ROUND_RECT
    prev_color = color

    def __init__(
        self,
        flowchart: "Flowchart",
        label: str,
        **kwargs,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creating node %s", label)
        self.flowchart = flowchart
        self.uid: str = kwargs.get("uid", None)
        if self.uid is None:
            raise ValueError("uid must be specified")

        self._label = label
        self.input_connectors: list[Connector] = []
        self.output_connectors: list[Connector] = []
        self.visited = False  # Add a visited attribute to keep track of visited nodes

        self.node_type_id = kwargs.get("node_type_id", None)
        if self.node_type_id is None:
            raise ValueError("node_type_id must be specified")

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, NodeBase):
            return self.uid == __o.uid
        return False

    def __hash__(self) -> int:
        return hash(self.uid)

    @property
    def connectors(self) -> list["Connector"]:
        """All connectors attached to this node"""
        return self.input_connectors + self.output_connectors

    @classmethod
    def deserialize(cls, flowchart: "Flowchart", data: dict):
        return cls(
            flowchart,
            **data,
        )

    @property
    def label(self) -> str:
        """Name of the node. Used for snapshotting."""
        return self._label

    @label.setter
    def label(self, label: str):
        self._label = label

    def begin_add_connector(self):
        """
        Start adding a connector to this node.
        Creates a temporary connector that follows the mouse.
        """
        self.flowchart.begin_add_connector(self)

    @abstractmethod
    def run_subclass(self, before_result: Any, state: State) -> str | None:
        """
        Code that will be run when the node is executed.
        """

    def before(self, state: State) -> Any:
        """
        Blocking method called before main node execution.
        """

    def run_node(self, before_result: Any, state: State) -> str:
        """
        Run the node and all nodes connected to it
        Handles setting the snapshot and returning the output.
        """
        state.snapshot[self.label] = state.snapshot.get(self.label, "")
        try:
            output: str = self.run_subclass(before_result, state)
        except Exception as node_exception:
            state.exception = True
            output = f"Error in node: {node_exception}"
        state.snapshot[self.label] = output
        state.result = output
        return output

    def serialize(self) -> dict[str, Any]:
        return {
            "uid": self.uid,
            "label": self.label,
            "node_type": self.__class__.__name__,
            "node_type_id": self.node_type_id,
            "graph_id": self.flowchart.uid,
            "metadata": self.get_options(),
        }

    def delete(self):
        """
        Delete the node and all connectors attached to it.
        """
        self.logger.info(f"Deleting node {self.label}")
        self.flowchart.remove_node(self)

    def copy(self) -> "NodeBase":
        """
        Create a copy of the node, without copying the connectors.
        """
        self.logger.info(f"Copying node {self.label}")
        data = self.serialize()
        data["label"] = f"{data['label']} copy"
        new_node = self.deserialize(self.flowchart, data)
        return new_node

    def get_children(self) -> list["NodeBase"]:
        """
        Return all child nodes of this node.
        """
        return [connector.next for connector in self.output_connectors]

    def edit_options(self, event):
        """
        Callback for the edit options button.
        Doesn't do anything by default.
        """

    def cost(self, state: State) -> float:
        """
        The cost of running this node in dollars.
        Adds the label to the snapshot as well for
        prompt formatting.
        """
        state.snapshot[self.label] = ""
        return 0.0

    @staticmethod
    def get_option_keys() -> list[str]:
        """
        Return the keys for the node options.
        """
        return ["label"]

    @classmethod
    def description(cls) -> str:
        """
        Return the description for the node, stored in the docstring.
        """
        return cls.__doc__ or ""

    def get_options(self) -> dict[str, Any]:
        """
        Return the options for the node.
        """
        options = {}
        for key in self.get_option_keys():
            options[key] = getattr(self, key)
            if isinstance(options[key], Serializable):
                options[key] = options[key].serialize()
            else:
                options[key] = options[key]
        return options
