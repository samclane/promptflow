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

    @staticmethod
    def get_option_keys() -> list[str]:
        return OpenAINode.get_option_keys() + ["dummy_string"]
