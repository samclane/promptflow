"""
Simulates an LLMNode, but does not actually send any data to the LLM.
"""
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
