"""
Handles long term memory storage and retrieval.
"""

from abc import ABC
import os
from uuid import uuid4
from typing import Any, Optional

import pinecone
from InstructorEmbedding import INSTRUCTOR

from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.state import State


class MemoryNode(NodeBase, ABC):
    pass


class PineconeNode(MemoryNode, ABC):
    """
    Handles data in Pinecone. Uses InstructorEmbedding to encode data.
    Dimensions: 768
    """

    index: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = kwargs.get("index", None)

    def embed(self, state: State) -> Any:
        instructor = INSTRUCTOR("hkunlp/instructor-large")
        embedding = instructor.encode(state.result)
        return embedding

    def run_subclass(self, before_result: Any, state) -> str:
        pinecone.init(
            api_key=os.environ["PINECONE_API_KEY"],
            environment=os.environ["PINECONE_ENVIRONMENT"],
        )
        return state.result


class PineconeInsertNode(PineconeNode):
    """
    Inserts data into Pinecone
    """

    def run_subclass(self, before_result: Any, state) -> str:
        super().run_subclass(before_result, state)
        if self.index is None:
            raise ValueError("Index must be set")
        index = pinecone.Index(self.index)
        embedding = self.embed(state)
        index.upsert([(uuid4(), embedding, {"text": state.result})])
        return state.result


class PineconeQueryNode(PineconeNode):
    """
    Queries data from Pinecone
    """

    k = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.k = kwargs.get("k", 1)

    def run_subclass(self, before_result: Any, state) -> str:
        super().run_subclass(before_result, state)
        if self.index is None:
            raise ValueError("Index must be set")
        index = pinecone.Index(self.index)
        embedding = self.embed(state.result)
        results = index.query(embedding, k=self.k, include_metadata=True)
        result = ""
        for match in results["matches"]:
            result += f"{match['metadata']['text']}\n"
        return result
