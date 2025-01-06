"""
Interact with word embeddings
"""
import csv
import logging
import os
import time
from abc import ABC
from typing import TYPE_CHECKING, Any, List, Optional

import hnswlib
import numpy as np
from InstructorEmbedding import INSTRUCTOR

from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.themes import monokai

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart


class EmbeddingsDatabaseSingleton:
    """
    Holds the collection of embeddings in single instance, like a database
    """

    _instance: Optional["EmbeddingsDatabaseSingleton"] = None
    index: hnswlib.Index
    index_file: Optional[str]
    filename: str
    content_index: dict
    label_file: Optional[str]
    instructor_model: INSTRUCTOR

    def __new__(cls) -> "EmbeddingsDatabaseSingleton":
        cls.logger = logging.getLogger(__name__)
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # try and load existing collection
            cls._instance.index = hnswlib.Index(space="l2", dim=768)
            cls._instance.index_file = None
            cls._instance.content_index = {}
            cls._instance.label_file = None
            cls._instance.instructor_model = INSTRUCTOR("hkunlp/instructor-large")
        return cls._instance


class EmbeddingNode(NodeBase, ABC):
    """
    Base class for Embedding nodes
    """

    node_color = monokai.GREEN

    def __init__(
        self,
        flowchart: "Flowchart",
        label: str,
        **kwargs,
    ):
        super().__init__(
            flowchart,
            label,
            **kwargs,
        )
        self.collection: EmbeddingsDatabaseSingleton = EmbeddingsDatabaseSingleton()

    def oai_embeddings(self, string: str) -> List[float]:
        """
        Get the openai ada embeddings for a string
        """
        raise DeprecationWarning(
            "This is deprecated; use instructor_embeddings instead"
        )
        # response = openai.Embedding.create(
        #     input=string,
        #     model="text-embedding-ada-002",
        # )
        # embeddings = response["data"][0]["embedding"]
        # return embeddings

    def instructor_embeddings(self, string: str) -> List[float]:
        """
        Get the instructOR embeddings for a string
        """
        return self.collection.instructor_model.encode(string)

    def embeddings(self, string: str) -> List[float]:
        """
        Wrap the embeddings function to allow for different models
        """
        return self.instructor_embeddings(string)

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["index_file", "label_file"]


class EmbeddingInNode(EmbeddingNode):
    """
    Takes data from a node and puts it into an hnswlib index
    """

    def run_subclass(self, before_result: Any, state) -> str:
        new_id = len(self.collection.content_index)
        self.collection.content_index[new_id] = state.result
        self.collection.index.add_items(
            np.array(self.embeddings(state.result)).reshape(1, -1), [new_id]
        )

        # Save index and mapping to files
        self.collection.index.save_index(self.collection.filename)
        with open(self.collection.label_file, "w") as f:
            csv.writer(f).writerows(self.collection.content_index.items())

        return state.result


class EmbeddingQueryNode(EmbeddingNode):
    """
    Queries an hnswlib index and returns the result
    """

    n_results: int = 1
    result_separator: str = "\n"
    options_popup = None

    def __init__(
        self,
        flowchart: "Flowchart",
        label: str,
        **kwargs,
    ):
        super().__init__(
            flowchart,
            label,
            **kwargs,
        )
        self.n_results = kwargs.get("n_results", 1)
        self.result_separator = kwargs.get("result_separator", "\n")

    def query(self, query_embeddings: list[float], n_results):
        """
        Query the embeddings using hnswlib
        """
        st = time.process_time()
        query_embeddings = np.array(query_embeddings)
        indices, distances = self.collection.index.knn_query(
            query_embeddings.reshape(1, -1), k=n_results
        )

        output = []
        for index in indices[0]:
            output.append(
                {"document": self.collection.content_index[index], "id": index}
            )

        print("query time", time.process_time() - st)
        return output

    def run_subclass(self, before_result: Any, state) -> str:
        results = self.query(
            query_embeddings=self.embeddings(state.result),
            n_results=self.n_results,
        )
        if len(results) == 0:
            return ""
        # return results["documents"][0][0]  # type: ignore
        # return self.result_separator.join(map(lambda x: x["document"], results))  # type: ignore
        return_string = ""
        for result in results:
            doc = result["document"]
            for k, v in doc.items():
                return_string += f"{k}: {v}" + self.result_separator
        return return_string

    def serialize(self):
        return super().serialize() | {
            "n_results": self.n_results,
            "result_separator": self.result_separator,
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["n_results", "result_separator"]


class EmbeddingsIngestNode(EmbeddingNode):
    """
    When pointed at a json file, will read all values into database
    TODO: this is a hack and only needs to be run once
    """

    def __init__(
        self,
        flowchart: "Flowchart",
        label: str,
        **kwargs,
    ):
        super().__init__(
            flowchart,
            label,
            **kwargs,
        )
        self.filename = kwargs.get("filename", "")
        self.label_file = kwargs.get("label_file", "")
        self.options_popup = None
        self.rows = kwargs.get("rows", [])

    def run_subclass(self, before_result: Any, state) -> str:
        self.collection.index.load_index(self.filename)
        with open(self.label_file, "r") as f:
            csv_reader = csv.DictReader(f, fieldnames=self.rows)
            self.collection.content_index = {}
            for i, row in enumerate(csv_reader):
                self.collection.content_index[i] = {
                    row_name: row for row_name in self.rows if row_name in row.keys()
                }
        return state.result

    def serialize(self):
        # convert filename to relative path
        # start path is directory of execution
        self.filename = os.path.relpath(self.filename, ".")
        self.label_file = os.path.relpath(self.label_file, ".")
        return super().serialize() | {
            "filename": self.filename,
            "label_file": self.label_file,
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["filename", "label_file"]
