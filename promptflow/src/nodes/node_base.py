"""
Base class for all nodes
"""
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from promptflow.src.serializable import Serializable
from promptflow.src.state import State
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.connectors.connector import Connector
    from promptflow.src.flowchart import Flowchart


class NodeBase(Serializable, ABC):
    """
    Represents a node in the flowchart, which could be a prompt, an llm, traditional code, etc.
    """

    node_color = monokai.WHITE
    prev_color = node_color
    size_px: int = 50  # arbitrary default size

    def __init__(
        self,
        flowchart: "Flowchart",
        label: str,
        **kwargs,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creating node %s", label)
        self.flowchart = flowchart
        self.id: str = kwargs.get("id", uuid4().hex)

        self._label = label
        self.input_connectors: list[Connector] = []
        self.output_connectors: list[Connector] = []
        self.visited = False  # Add a visited attribute to keep track of visited nodes

        # create the label
        self.center_y = kwargs.get("center_y", 0)
        self.center_x = kwargs.get("center_x", 0)

        self.node_type_id = kwargs.get("node_type_id", None)
        if self.node_type_id is None:
            raise ValueError("node_type_id must be specified")

    @classmethod
    def get_all_node_types(cls) -> list[str]:
        """
        Return a list of all node types.
        """
        # get all subclasses of NodeBase
        subclasses = NodeBase.__subclasses__()
        # filter out abstract classes
        subclasses = [
            subclass for subclass in subclasses if not subclass.__abstractmethods__
        ]
        # get the name of each subclass
        return [subclass.__name__ for subclass in subclasses]

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, NodeBase):
            return self.id == __o.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

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

    def save_to_db(self):
        pass

    def get_center(
        self, offset_x: float = 0, offset_y: float = 0
    ) -> tuple[float, float]:
        """
        Node is defined by its top left and bottom right coordinates.
        This function returns the center of the node based on those coordinates.
        """
        return self.center_x + offset_x, self.center_y + offset_y

    def begin_add_connector(self):
        """
        Start adding a connector to this node.
        Creates a temporary connector that follows the mouse.
        """
        self.flowchart.begin_add_connector(self)

    def start_drag(self, event):
        """
        Update the flowchart's selected node and start dragging the node by
        updating the node's x and y coordinates.
        """
        self.flowchart.selected_element = self
        self.center_x = event.x
        self.center_y = event.y

    def on_drag(self, event):
        """
        Continuously update the node's position while dragging.
        Update all connectors to follow the node.
        """
        self.center_x = event.x
        self.center_y = event.y

    def stop_drag(self, _):
        """
        Required to be able to drag the node.
        """

    @abstractmethod
    def run_subclass(self, before_result: Any, state: State) -> str:
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
        output: str = self.run_subclass(before_result, state)
        state.snapshot[self.label] = output
        state.result = output
        return output

    def serialize(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "uid": self.id,
            "label": self.label,
            "center_x": self.center_x,
            "center_y": self.center_y,
            "classname": self.__class__.__name__,
            "node_type_id": self.node_type_id,
            "metadata": {},
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
        return [connector.node2 for connector in self.output_connectors]

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

    def move_to(self, x: float, y: float):
        """
        Move the node to the given coordinates.
        """
        self.center_x = x
        self.center_y = y

    def get_options(self) -> dict[str, Any]:
        """
        Return the options for the node.
        """
        return {
            "options": {
                "label": self.label,
                "center_x": self.center_x,
                "center_y": self.center_y,
            },
            "editor": None,
        }
