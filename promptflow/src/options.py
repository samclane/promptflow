"""
Manage and validate options for the promptflow application
"""
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from promptflow.src.serializable import Serializable


class Options(BaseModel, Serializable):
    """Options for PromptFlow"""

    def serialize(self) -> dict:
        return self.dict()

    @classmethod
    def deserialize(cls, *args, **kwargs) -> "Options":
        return cls(*args, **kwargs)

    def save(self, path: str):
        with open(path, "w") as options_file:
            options_file.write(self.json())
