"""
Simulates an LLMNode, but does not actually send any data to the LLM.
"""
from typing import Any

from promptflow.src.nodes.llm_node import OpenAINode
from promptflow.src.state import State


class DummyNode(OpenAINode):
    """
    Simulates an LLMNode, but does not actually send any data to the LLM.
    """

    dummy_string: str = "dummy string"

    def _chat_completion(self, prompt: str, state: State) -> str:
        return self.dummy_string

    def _completion(self, prompt: str, state: State) -> str:
        return self.dummy_string

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["dummy_string"] = self.dummy_string
        return base_options
