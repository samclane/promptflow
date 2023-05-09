"""
Nodes for handling structured data.
"""
from abc import ABC, abstractmethod
import json
import tkinter as tk
from typing import Any
import jsonschema
from promptflow.src.dialogues.text_input import TextInput
from promptflow.src.nodes.node_base import NodeBase


class StructuredDataNode(NodeBase, ABC):
    """
    Base class for nodes that handle structured data.
    """

    schema = None
    text_input = None

    @abstractmethod
    def validate(self, data):
        """
        Validate the data.
        """

    def run_subclass(
        self, before_result: Any, state, console: tk.scrolledtext.ScrolledText
    ) -> str:
        validation: str = self.validate(state.result)
        return validation


class JsonNode(StructuredDataNode):
    """
    Node that validates JSON.
    """

    def edit_options(self, event):
        """
        Allow user to edit the schema.
        """
        # create a text input dialogue
        self.text_input = TextInput(self.canvas, self.flowchart, self.schema)
        self.text_input.set_callback(self.save_options)

    def validate(self, data):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return "Invalid JSON"
        try:
            jsonschema.validate(data, self.schema)
        except jsonschema.ValidationError as e:
            return "Validation error: " + str(e)
        except jsonschema.SchemaError as e:
            return "Schema error: " + str(e)
        return data

    def save_options(self):
        """
        Save the schema.
        """
        self.schema = json.loads(self.text_input.get_text().text)
        self.text_input.destroy()
        self.text_input = None
