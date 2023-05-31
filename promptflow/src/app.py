"""
Primary application class. This class is responsible for creating the
window, menu, and canvas. It also handles the saving and loading of
flowcharts.
"""
import json
import logging
import sys
from fastapi import FastAPI, Response, File, UploadFile
from PIL import Image, ImageTk
import networkx as nx
import os
from typing import Optional
import zipfile
from PIL import ImageGrab
from promptflow.src.command import (
    CommandManager,
    AddConnectionCommand,
    RemoveConnectionCommand,
    AddNodeCommand,
    RemoveNodeCommand,
)
from promptflow.src.connectors.connector import Connector
from promptflow.src.cursor import FlowchartCursor

from promptflow.src.flowchart import Flowchart
from promptflow.src.nodes.audio_node import ElevenLabsNode, WhispersNode
from promptflow.src.nodes.date_node import DateNode
from promptflow.src.nodes.env_node import EnvNode, ManualEnvNode
from promptflow.src.nodes.http_node import HttpNode, JSONRequestNode, ScrapeNode
from promptflow.src.nodes.image_node import (
    DallENode,
    CaptionNode,
    OpenImageFile,
    JSONImageFile,
    SaveImageNode,
)
from promptflow.src.nodes.memory_node import PineconeInsertNode, PineconeQueryNode
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.nodes.db_node import (
    PGMLNode,
    PGGenerateNode,
    SQLiteQueryNode,
    PGQueryNode,
)
from promptflow.src.nodes.output_node import FileOutput, JSONFileOutput
from promptflow.src.nodes.regex_node import RegexNode, TagNode
from promptflow.src.nodes.start_node import InitNode, StartNode
from promptflow.src.nodes.prompt_node import PromptNode
from promptflow.src.nodes.func_node import FuncNode
from promptflow.src.nodes.llm_node import ClaudeNode, OpenAINode, GoogleVertexNode
from promptflow.src.nodes.random_number import RandomNode
from promptflow.src.nodes.history_node import (
    HistoryNode,
    ManualHistoryNode,
    HistoryWindow,
    WindowedHistoryNode,
    DynamicWindowedHistoryNode,
)
from promptflow.src.nodes.embedding_node import (
    EmbeddingInNode,
    EmbeddingQueryNode,
    EmbeddingsIngestNode,
)
from promptflow.src.nodes.input_node import FileInput, InputNode, JSONFileInput
from promptflow.src.nodes.server_node import ServerInputNode
from promptflow.src.nodes.structured_data_node import JsonNode, JsonerizerNode
from promptflow.src.nodes.test_nodes import AssertNode, LoggingNode, InterpreterNode
from promptflow.src.nodes.websearch_node import SerpApiNode, GoogleSearchNode
from promptflow.src.options import Options
from promptflow.src.nodes.dummy_llm_node import DummyNode
from promptflow.src.state import State
from promptflow.src.themes import monokai
from promptflow.src.dialogues.app_options import AppOptions

app = FastAPI()


class App:
    """
    Primary application class. This class is responsible for creating the
    window, menu, and canvas. It also handles the saving and loading of
    flowcharts.
    """

    def __init__(self):
        self.logging_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.logger = logging.getLogger(__name__)

        logging.basicConfig(level=logging.DEBUG, format=self.logging_fmt)
        self.logger.info("Creating app")

    @app.get("/flowcharts/{flowchart_id}/run")
    def run_flowchart(self, flowchart_id: int) -> dict:
        """Execute the flowchart."""
        self.logger.info("Running flowchart")
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id)
        init_state = State()
        init_state = flowchart.initialize(init_state)
        final_state = flowchart.run(init_state)
        self.logger.info("Finished running flowchart")
        if final_state:
            return {"state": final_state.serialize()}
        else:
            return {"state": None}

    @app.get("/flowcharts/{flowchart_id}/stop")
    def stop_flowchart(self, flowchart_id: int):
        """Stop the flowchart."""
        self.logger.info("Stopping flowchart")
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id)
        flowchart.is_running = False
        flowchart.is_dirty = True
        return {"message": "Flowchart stopped"}

    @app.get("/flowcharts/{flowchart_id}/serialize")
    def serialize_flowchart(self, flowchart_id: int) -> dict:
        """Serialize the flowchart to JSON."""
        self.logger.info("Serializing flowchart")
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id)
        chart_json = json.dumps(flowchart.serialize(), indent=4)
        self.logger.info(chart_json)
        return {"flowchart": chart_json}

    @app.get("/flowcharts/{flowchart_id}/clear")
    def clear_flowchart(self, flowchart_id: int):
        """Clear the flowchart."""
        self.logger.info("Clearing flowchart")
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id)
        flowchart.clear()
        # self.output_console.delete("1.0", tk.END)
        return {"message": "Flowchart cleared"}

    @app.get("/flowcharts/{flowchart_id}/cost")
    def cost_flowchart(self, flowchart_id: int) -> dict:
        """Get the approx cost to run the flowchart"""
        self.logger.info("Getting cost of flowchart")
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id)
        state = State()
        cost = flowchart.cost(state)
        return {"cost": cost}

    @app.post("/flowcharts/{flowchart_id}/save_as")
    def save_as(self, flowchart_id: int) -> dict | Response:
        """
        Serialize the flowchart and save it to a file
        """
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id)
        filename = flowchart.name
        if filename:
            with zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(
                    "flowchart.json", json.dumps(flowchart.serialize(), indent=4)
                )
                # if there's an embedding ingest node, save the embedding
                for node in flowchart.nodes:
                    if isinstance(node, EmbeddingsIngestNode):
                        # write the embedding to the archive
                        archive.write(node.filename, arcname=node.filename)
                        archive.write(node.label_file, arcname=node.label_file)
                self.logger.info("Saved flowchart to %s", filename)
            with open(filename, "rb") as f:
                return Response(content=f.read(), media_type="application/zip")
        else:
            self.logger.info("No file selected to save to")
            return {"message": "No file selected to save to"}

    @app.post("/flowcharts/load_from")
    def load_from(self, file: UploadFile = File(...)) -> dict:
        """
        Read a json file and deserialize as a flowchart
        """
        if file.filename:
            with zipfile.ZipFile(file.filename, "r") as archive:
                with archive.open("flowchart.json") as loadfile:
                    data = json.load(loadfile)
                    # load the embedding if there is one
                    for node in data["nodes"]:
                        if node["classname"] == "EmbeddingsIngestNode":
                            # load the embedding
                            embed_file = archive.extract(
                                node["filename"], path=os.getcwd()
                            )
                            node["filename"] = embed_file
                            # load the labels
                            label_file = archive.extract(
                                node["label_file"], path=os.getcwd()
                            )
                            node["label_file"] = label_file
                    flowchart = Flowchart.deserialize(data)
                    return {"flowchart": flowchart.serialize()}
        else:
            self.logger.info("No file selected to load from")
            return {"message": "No file selected to load from"}

    @app.post("/nodes/{classname}/add")
    def add_node(self, classname: str, flowchart_id: int) -> dict:
        node = exec(f"{classname}()")
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id)
        flowchart.add_node(node)
        return {"message": "Node added"}

    @app.post("/nodes/{classname}/remove")
    def remove_node(self, classname: str, flowchart_id: int) -> dict:
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id)
        node = flowchart.get_node_by_id(classname)
        flowchart.remove_node(node)
