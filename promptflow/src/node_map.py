"""
Maps node names to node classes
"""
from typing import Dict, Type

from promptflow.src.nodes.audio_node import ElevenLabsNode, WhispersNode
from promptflow.src.nodes.date_node import DateNode
from promptflow.src.nodes.db_node import PGGenerateNode, PGQueryNode, SQLiteQueryNode
from promptflow.src.nodes.debug_nodes import AssertNode, InterpreterNode, LoggingNode
from promptflow.src.nodes.dummy_llm_node import DummyNode
from promptflow.src.nodes.embedding_node import (
    EmbeddingInNode,
    EmbeddingQueryNode,
    EmbeddingsIngestNode,
)
from promptflow.src.nodes.env_node import EnvNode, ManualEnvNode
from promptflow.src.nodes.func_node import FuncNode
from promptflow.src.nodes.history_node import (
    DynamicWindowedHistoryNode,
    HistoryNode,
    HistoryWindow,
    ManualHistoryNode,
    WindowedHistoryNode,
)
from promptflow.src.nodes.http_node import HttpNode, JSONRequestNode, ScrapeNode
from promptflow.src.nodes.image_node import (
    CaptionNode,
    DallENode,
    JSONImageFile,
    OpenImageFile,
    SaveImageNode,
)
from promptflow.src.nodes.input_node import FileInput, InputNode, JSONFileInput
from promptflow.src.nodes.llm_node import ClaudeNode, GoogleVertexNode, OpenAINode
from promptflow.src.nodes.memory_node import PineconeInsertNode, PineconeQueryNode
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.nodes.output_node import FileOutput, JSONFileOutput
from promptflow.src.nodes.prompt_node import PromptNode
from promptflow.src.nodes.random_number import RandomNode
from promptflow.src.nodes.server_node import ServerInputNode
from promptflow.src.nodes.start_node import InitNode, StartNode
from promptflow.src.nodes.structured_data_node import JsonerizerNode, JsonNode
from promptflow.src.nodes.websearch_node import GoogleSearchNode, SerpApiNode

node_map: Dict[str, Type[NodeBase]] = {
    "InitNode": InitNode,
    "StartNode": StartNode,
    "InputNode": InputNode,
    "FileInput": FileInput,
    "JSONFileInput": JSONFileInput,
    "FuncNode": FuncNode,
    "OpenAINode": OpenAINode,
    "ClaudeNode": ClaudeNode,
    "GoogleVertexNode": GoogleVertexNode,
    "DateNode": DateNode,
    "RandomNode": RandomNode,
    "HistoryNode": HistoryNode,
    "ManualHistoryNode": ManualHistoryNode,
    "HistoryWindow": HistoryWindow,
    "WindowedHistoryNode": WindowedHistoryNode,
    "DynamicWindowedHistoryNode": DynamicWindowedHistoryNode,
    "DummyNode": DummyNode,
    "PromptNode": PromptNode,
    "EmbeddingInNode": EmbeddingInNode,
    "EmbeddingQueryNode": EmbeddingQueryNode,
    "EmbeddingsIngestNode": EmbeddingsIngestNode,
    "AssertNode": AssertNode,
    "LoggingNode": LoggingNode,
    "InterpreterNode": InterpreterNode,
    "EnvNode": EnvNode,
    "ManualEnvNode": ManualEnvNode,
    "WhispersNode": WhispersNode,
    "ElevenLabsNode": ElevenLabsNode,
    "PGQueryNode": PGQueryNode,
    "SQLiteQueryNode": SQLiteQueryNode,
    "PGGenerateNode": PGGenerateNode,
    "JsonNode": JsonNode,
    "JsonerizerNode": JsonerizerNode,
    "SerpApiNode": SerpApiNode,
    "GoogleSearchNode": GoogleSearchNode,
    "FileOutput": FileOutput,
    "JSONFileOutput": JSONFileOutput,
    "HttpNode": HttpNode,
    "JSONRequestNode": JSONRequestNode,
    "ScrapeNode": ScrapeNode,
    "ServerInputNode": ServerInputNode,
    "PineconeInsertNode": PineconeInsertNode,
    "PineconeQueryNode": PineconeQueryNode,
    "DallENode": DallENode,
    "CaptionNode": CaptionNode,
    "OpenImageFile": OpenImageFile,
    "JSONImageFile": JSONImageFile,
    "SaveImageNode": SaveImageNode,
}

if __name__ == "__main__":
    # populate the database with the node_map
    from promptflow.src.postgres_interface import DatabaseConfig, PostgresInterface

    interface = PostgresInterface(
        DatabaseConfig(
            host="172.18.0.3",
            database="postgres",
            user="postgres",
            password="postgres",
        )
    )

    conn = interface.conn
    cur = interface.cursor
    for node_name in node_map:
        cur.execute(
            """
            INSERT INTO node_types (name) VALUES (%s) ON CONFLICT DO NOTHING
            """,
            (node_name,),
        )
    conn.commit()

    conn.close()
