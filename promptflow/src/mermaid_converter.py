from enum import Enum
from string import Template
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from promptflow.src.connectors.connector import Connector
    from promptflow.src.nodes.node_base import NodeBase


class Orientation(Enum):
    """Enum for the orientation of the flowchart"""

    TB = "TB"  # Top to bottom
    TD = "TD"  # Top down
    BT = "BT"  # Bottom to top
    RL = "RL"  # Right to left
    LR = "LR"  # Left to right


class MermaidNodeShape(Enum):
    """Enum for the shape of the node"""

    ROUND_RECT = Template('$uid["$label"]')
    STADIUM = Template('$uid(["$label"])')
    SUBROUTINE = Template('$uid[["$label"]]')
    CYLINDER = Template('$uid[("$label")]')
    CIRCLE = Template('$uid(("$label"))')
    FLAG = Template('$uid>"$label"]')
    RHOMBUS = Template('$uid{"$label"}')
    HEXAGON = Template('$uid{{"$label"}}')
    PARALLELOGRAM = Template('$uid[/"$label"/]')
    PARALLELOGRAM_ALT = Template('$uid[\\"$label"\\]')
    TRAPEZOID = Template('$uid[/"$label"\\]')
    TRAPEZOID_ALT = Template('$uid[\\"$label"/]')
    DOUBLE_CIRCLE = Template('$uid((("$label")))')


class MermaidConnectorShape(Enum):
    """Enum for the shape of the connector"""

    ARROW = Template("$uid --> $uid2")
    OPEN = Template("$uid --- $uid2")
    TEXT = Template('$uid-- "$label" ---$uid2')
    CODE = Template('$uid -->|"$label"|> $uid2')
    ARROW_TEXT = Template('$uid-->|"$label"|$uid2')
    ARROW_CODE = Template('$uid-- "$label"| -->$uid2')
    DOTTED = Template("$uid -.-> $uid2;")
    DOTTED_TEXT = Template('$uid -. "$label" .-> $uid2')
    THICK = Template("$uid ==> $uid2")
    THICK_TEXT = Template('$uid == "$label" ==> $uid')
    INVISIBLE = Template("$uid ~~~ $uid2")


class MermaidConverter:
    """Handles converting a flowchart to mermaid syntax"""

    def __init__(self, flowchart, orientation=Orientation.TD):
        self.flowchart = flowchart
        self.orientation = orientation

    def sanitize_uid(self, uid) -> str:
        """Mermaid does not allow spaces in node names, so we replace them with underscores"""
        return uid.replace(" ", "_")

    def convert_node(self, node: "NodeBase") -> str:
        """Converts a node to mermaid syntax"""
        return f"\t{node.mermaid_shape.value.substitute(uid=self.sanitize_uid(node.uid), label=node.label)}\n"

    def convert_connector(self, connector: "Connector") -> str:
        """Converts a connector to mermaid syntax"""
        if connector.condition_label:
            return f"\t{connector.mermaid_shape.value.substitute(uid=self.sanitize_uid(connector.prev.uid), label=connector.condition_label, uid2=self.sanitize_uid(connector.next.uid))}\n"
        else:
            return f"\t{connector.mermaid_shape.value.substitute(uid=self.sanitize_uid(connector.prev.uid), uid2=self.sanitize_uid(connector.next.uid))}\n"

    def to_mermaid(self) -> str:
        """Converts the flowchart to mermaid syntax"""
        mermaid_str = f"flowchart {self.orientation.value}\n"
        for node in self.flowchart.nodes:
            mermaid_str += self.convert_node(node)
        for connector in self.flowchart.connectors:
            mermaid_str += self.convert_connector(connector)
        return mermaid_str
