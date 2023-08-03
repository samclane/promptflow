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

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["min", "max"]
