import random
from typing import Any

from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.themes import monokai


class RandomNode(NodeBase):
    """
    Injects a random number (min-max) into state
    """

    node_color = monokai.PINK
    min: int = 0
    max: int = 100

    def run_subclass(self, before_result: Any, state) -> str:
        r = random.randint(self.min, self.max)
        return str(r)

    def serialize(self):
        return super().serialize() | {
            "min": self.min,
            "max": self.max,
        }

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["min"] = self.min
        base_options["options"]["max"] = self.max
        return base_options
