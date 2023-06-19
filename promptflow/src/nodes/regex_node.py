"""
Nodes that handle regular expressions and parsing text, usually 
from LLM output (but not always)
"""
import re
from typing import Any

from promptflow.src.nodes.node_base import NodeBase


class RegexNode(NodeBase):
    """
    Node that handles regular expressions
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )
        self.regex = kwargs.get("regex", "")

    def run_subclass(self, before_result: Any, state) -> str:
        """
        Runs the regex on the state
        """
        self.logger.info("Regex node %s has state %s", self.label, state)
        search = re.search(self.regex, state.result)
        if search is None:
            return ""
        return search.group(0)

    def serialize(self) -> dict:
        return super().serialize() | {
            "regex": self.regex,
        }

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["regex"] = self.regex
        return base_options


class TagNode(NodeBase):
    """
    Gets the text in-between two tags
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_tag = kwargs.get("start_tag", "")
        self.end_tag = kwargs.get("end_tag", "")

    def run_subclass(self, before_result: Any, state) -> str:
        """
        Extracts the text in-between the start and end tags from the state
        """
        self.logger.info("Tag node %s has state %s", self.label, state)
        content = state.result
        start_index = content.find(self.start_tag)
        end_index = content.find(self.end_tag, start_index)

        if start_index == -1 or end_index == -1:
            return ""

        start_index += len(self.start_tag)
        return content[start_index:end_index]

    def serialize(self) -> dict:
        return super().serialize() | {
            "start_tag": self.start_tag,
            "end_tag": self.end_tag,
        }

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["start_tag"] = self.start_tag
        base_options["options"]["end_tag"] = self.end_tag
        return base_options
