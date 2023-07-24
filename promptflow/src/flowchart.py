"""
This module contains the Flowchart class, which manages the nodes and connectors of a flowchart.
"""
from __future__ import annotations

import logging
import threading
import time
from queue import Queue
from typing import TYPE_CHECKING, Any, Callable, Optional

import networkx as nx

from promptflow.src.connectors.connector import Connector
from promptflow.src.connectors.partial_connector import PartialConnector
from promptflow.src.node_map import node_map
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.nodes.start_node import InitNode, StartNode

if TYPE_CHECKING:
    from promptflow.src.postgres_interface import DBInterface

from promptflow.src.state import State
from promptflow.src.text_data import TextData


class Flowchart:
    """
    Holds the nodes and connectors of a flowchart.
    """

    interface: DBInterface
    uid: str
    name: str
    created: float
    nodes: list[NodeBase]
    connectors: list[Connector]

    def __init__(
        self,
        interface: DBInterface,
        uid: str,
        name: Optional[str] = None,
        created: Optional[float] = None,
    ):
        self.interface = interface
        self.uid = uid
        if not self.uid:
            raise ValueError("Flowchart id not provided")
        self.name = name or "Untitled"
        self.created = created or time.time()
        self.graph = nx.DiGraph()
        self.nodes: list[NodeBase] = []
        self.connectors: list[Connector] = []
        self.text_data_registry: dict[str, TextData] = {}
        self.logger = logging.getLogger(__name__)

        self._selected_element: Optional[NodeBase | Connector] = None
        self._partial_connector: Optional[PartialConnector] = None

        self.is_dirty = False
        self.is_running = False

    @classmethod
    def get_flowchart_by_uid(cls, uid, interface: DBInterface):
        """
        Return a flowchart by uid
        """
        return interface.get_flowchart_by_uid(uid)

    @classmethod
    def deserialize(
        cls, interface: DBInterface, data: dict[str, Any], pan=(0, 0)
    ) -> Flowchart:
        """
        Deserialize a flowchart from a dict
        """
        flowchart = cls(
            interface,
            uid=data["uid"],
            name=data.get("label", "Untitled"),
            created=data.get("created", time.time()),
        )
        for node_data in data["nodes"]:
            node = node_map[node_data["node_type"]].deserialize(flowchart, node_data)
            x_offset = pan[0]
            y_offset = pan[1]
            flowchart.add_node(node, (x_offset, y_offset))
        for connector_data in data["branches"]:
            prev = flowchart.find_node(connector_data["prev"])
            next = flowchart.find_node(connector_data["next"])
            connector = Connector(
                prev,
                next,
                connector_data.get("conditional", ""),
                uid=connector_data["uid"],
            )
            flowchart.add_connector(connector)
        flowchart.is_dirty = False
        return flowchart

    @property
    def selected_element(self) -> Optional[NodeBase | Connector]:
        """
        Return last touched node
        """
        return self._selected_element

    @selected_element.setter
    def selected_element(self, elem: Optional[NodeBase | Connector]):
        self.logger.info("Selected element changed to %s", elem.label if elem else None)
        self._selected_element = elem

    @property
    def start_node(self) -> StartNode:
        """
        Find and return the node with the class StartNode
        """
        start_nodes = [node for node in self.nodes if isinstance(node, StartNode)]
        if len(start_nodes) == 0:
            raise ValueError("No start node found")

        if len(start_nodes) == 1:
            return start_nodes[0]

        # sort by number of input connectors
        start_nodes.sort(key=lambda node: len(node.input_connectors))
        return start_nodes[0]

    @property
    def init_node(self) -> Optional[InitNode]:
        """
        Find and returns the single-run InitNode
        """
        try:
            return [node for node in self.nodes if isinstance(node, InitNode)][0]
        except IndexError:
            return None

    def find_node(self, node_id: str) -> NodeBase:
        """
        Given a node id, find and return the node
        """
        for node in self.nodes:
            if node.uid == node_id:
                return node
        raise ValueError(f"No node with id {node_id} found")

    def add_node(self, node: NodeBase, offset: tuple[int, int] = (0, 0)) -> NodeBase:
        """
        Safely insert a node into the flowchart
        """
        while node in self.nodes:
            self.logger.debug("Duplicate node found, adding (copy) to label...")
            node.label += " (copy)"
        # todo handle offset
        self.nodes.append(node)
        self.graph.add_node(node)
        self.selected_element = node
        self.is_dirty = True
        return node

    def add_connector(self, connector: Connector) -> Connector:
        """
        Safely insert a connector into the flowchart
        """
        # check for duplicate connectors
        self.logger.debug(f"Adding connector {connector}")
        self.connectors.append(connector)
        self.graph.add_edge(connector.prev, connector.next)
        self.selected_element = connector
        self.is_dirty = True
        return connector

    def initialize(self, state: State) -> Optional[State]:
        """
        Initialize the flowchart
        """
        self.is_running = True
        init_node: Optional[InitNode] = self.init_node
        if not init_node or init_node.run_once:
            self.logger.info("Flowchart already initialized")
            return state
        queue: Queue[NodeBase] = Queue()
        queue.put(init_node)
        return self.run(state, queue)

    def run(
        self,
        state: Optional[State],
        queue: Optional[Queue[NodeBase]] = None,
        logging_function: Callable[[str], None] = lambda x: None,
    ) -> Optional[State]:
        """
        Given a state, run the flowchart and update the state
        """
        self.logger.info("Running flowchart")
        if not queue:
            queue = Queue()
            queue.put(self.start_node)
            self.is_running = True
        if queue.empty() and not self.is_running:
            queue.put(self.start_node)
            self.is_running = True
        state = state or State()

        if not queue.empty():
            if not self.is_running:
                self.logger.info("Flowchart stopped")
                self.is_running = False
                return state
            cur_node: NodeBase = queue.get()
            self.logger.info(f"Running node {cur_node.label}")
            before_result = cur_node.before(state)
            try:
                thread = threading.Thread(
                    target=cur_node.run_node,
                    args=(before_result, state),
                    daemon=True,
                )
                thread.start()
                while thread.is_alive():
                    pass
                thread.join()
                output = state.result
                logging_function(f"Node {cur_node.label} output: {str(output)}")
            except Exception as node_err:
                self.logger.error(
                    f"Error running node {cur_node.label}: {node_err}", exc_info=True
                )
                return state
            self.logger.info(f"Node {cur_node.label} output: {output}")

            if output is None:
                self.logger.info(
                    f"Node {cur_node.label} output is None, stopping execution"
                )
                return state

            for connector in cur_node.output_connectors:
                if connector.condition.text.strip():
                    # evaluate condition and only add node2 to queue if condition is true
                    exec(
                        connector.condition.text.strip(),
                        dict(globals()),
                        state.snapshot,
                    )
                    try:
                        cond = state.snapshot["main"](state)  # type: ignore
                    except Exception as node_err:
                        # log complete error traceback
                        self.logger.error(
                            f"Error evaluating condition: {node_err}",
                            exc_info=True,
                        )
                        break
                    self.logger.info(
                        f"Condition {connector.condition} evaluated to {cond}"
                    )
                else:
                    cond = True
                if cond:
                    # if connector.node2 not in queue:
                    if queue.queue.count(connector.next) == 0:
                        queue.put(connector.next)
                        self.run(state, queue)
                    self.logger.info(f"Added node {connector.next.label} to queue")

        if queue.empty():
            self.logger.info("Flowchart stopped")
            self.is_running = False
            return state

    def begin_add_connector(self, node: NodeBase):
        """
        Start adding a connector from the given node.
        """
        if self._partial_connector:
            self._partial_connector.delete(None)
        self._partial_connector = PartialConnector(self, node)

    def serialize(self) -> dict[str, Any]:
        """
        Write the flowchart to a dictionary
        """
        data: dict[str, Any] = {
            "uid": self.uid,
            "label": self.name,
            "created": str(self.created),
        }
        data["nodes"] = []
        for node in self.nodes:
            data["nodes"].append(node.serialize())
        data["branches"] = []
        for connector in self.connectors:
            data["branches"].append(connector.serialize())
        return data

    def remove_node(self, node: NodeBase) -> None:
        """
        Remove a node and all connectors connected to it.
        """
        self.logger.info(f"Removing node {node}")
        if node in self.nodes:
            self.nodes.remove(node)
        # remove all connectors connected to this node
        for other_node in self.nodes:
            for connector in other_node.connectors:
                if connector.prev == node or connector.next == node:
                    connector.delete()
                    self.graph.remove_edge(connector.prev, connector.next)
                    if connector in other_node.input_connectors:
                        other_node.input_connectors.remove(connector)
                    if connector in other_node.output_connectors:
                        other_node.output_connectors.remove(connector)
        for connector in self.connectors:
            if connector.prev == node or connector.next == node:
                connector.delete()
                self.graph.remove_edge(connector.prev, connector.next)
        self.graph.remove_node(node)
        self.is_dirty = True

    def clear(self) -> None:
        """
        Clear the flowchart.
        """
        self.logger.info("Clearing")
        for node in self.nodes:
            node.delete()
        self.nodes = []
        for connector in self.connectors:
            connector.delete()
        self.connectors = []
        self.graph.clear()
        self.is_dirty = True

    def register_text_data(self, text_data: TextData) -> None:
        """
        On creation of a TextData object, register it with the flowchart.
        """
        if text_data.label:
            self.logger.debug(f"Registering text data {text_data.label}")
            self.text_data_registry[text_data.label] = text_data

    def cost(self, state: State) -> float:
        """
        Return the cost of the flowchart.
        """
        cost = 0
        for node in self.nodes:
            cost += node.cost(state)
        return cost

    def to_mermaid(self) -> str:
        """
        Return a mermaid string representation of the flowchart.
        """
        mermaid_str = "graph TD\n"
        for node in self.nodes:
            mermaid_str += f"{node.uid}({node.label})\n"
        for connector in self.connectors:
            if connector.condition_label:
                mermaid_str += f"{connector.prev.uid} -->|{connector.condition_label}| {connector.next.uid}\n"
            else:
                mermaid_str += f"{connector.prev.uid} --> {connector.next.uid}\n"

        return mermaid_str

    def to_graph_ml(self) -> str:
        """
        Convert the flowchart to graphml
        """
        graphml_string = """<?xml version="1.0" encoding="UTF-8"?>
        <graphml xmlns="http://graphml.graphdrawing.org/xmlns">
        """
        for node in self.nodes:
            graphml_string += f"""<node id="{node.uid}">
            <data key="d0">{node.label}</data>
            </node>
            """
        for connector in self.connectors:
            if connector.condition_label:
                graphml_string += f"""<edge source="{connector.prev.uid}" target="{connector.next.uid}">
                <data key="d0">{connector.condition_label}</data>
                </edge>
                """
            else:
                graphml_string += f"""<edge source="{connector.prev.uid}" target="{connector.next.uid}"/>
                """
        graphml_string += "\r</graphml>"
        return graphml_string

    def arrange_tree(self, root: NodeBase, x=0.0, y=0.0, x_gap=60.0, y_gap=60.0):
        """
        Arrange all nodes in a tree-like structure.
        """
        root.visited = True
        root.move_to(x, y)
        if root.get_children():
            next_y = y + root.size_px + y_gap
            total_width = (
                sum(child.size_px + x_gap for child in root.get_children()) - x_gap
            )
            next_x = x + (root.size_px - total_width) / 2
            for child in root.get_children():
                if not child.visited:
                    self.arrange_tree(child, next_x, next_y, x_gap, y_gap)
                    next_x += child.size_px + x_gap

    def arrange_networkx(self, algorithm, scale=1.0):
        """
        Arrange all nodes using a networkx algorithm.
        """
        kwargs = {}
        if algorithm == nx.layout.bipartite_layout:
            kwargs["nodes"] = self.graph.nodes
        pos = algorithm(self.graph, scale=self.nodes[0].size_px * scale, **kwargs)
        for node in self.nodes:
            node.move_to(pos[node][0], pos[node][1])
        return pos
