"""
Nodes for handling structured data.
"""
import ast
import json
from abc import ABC, abstractmethod
from typing import Any

import jsonschema

from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.state import State


class StructuredDataNode(NodeBase, ABC):
    """
    Base class for nodes that handle structured data.
    """

    schema = None
    text_input = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = kwargs.get("schema", None)

    @abstractmethod
    def validate(self, data):
        """
        Validate the data.
        """

    def run_subclass(self, before_result: Any, state: State) -> str:
        validation: str = self.validate(state.result)
        return validation

    def serialize(self):
        return super().serialize() | {"schema": self.schema}

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["schema"] = self.schema
        return base_options


class JsonNode(StructuredDataNode):
    """
    Node that validates JSON into a python dictionary.
    """

    schema = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = kwargs.get("schema", None)

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

    def serialize(self):
        return super().serialize() | {"schema": self.schema}

    def get_options(self) -> dict[str, Any]:
        base_options = super().get_options()
        base_options["options"]["schema"] = self.schema
        return base_options


class JsonerizerNode(NodeBase):
    """
    Node that converts a python dictionary into JSON.
    """

    def run_subclass(self, before_result: Any, state) -> str:
        d: dict = ast.literal_eval(state.result)
        return json.dumps(d, indent=4)
