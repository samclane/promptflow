"""
Primary application class. This class is responsible for creating the
window, menu, and canvas. It also handles the saving and loading of
flowcharts.
"""
import json
import logging
import sqlite3
from fastapi import FastAPI, Response, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import zipfile
from promptflow.src.flowchart import Flowchart

from promptflow.src.nodes.embedding_node import (
    EmbeddingsIngestNode,
)
from promptflow.src.state import State
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.nodes.start_node import InitNode, StartNode
from promptflow.src.nodes.input_node import InputNode, FileInput, JSONFileInput
from promptflow.src.nodes.func_node import FuncNode
from promptflow.src.nodes.llm_node import OpenAINode, ClaudeNode, GoogleVertexNode
from promptflow.src.nodes.date_node import DateNode
from promptflow.src.nodes.random_number import RandomNode
from promptflow.src.nodes.history_node import (
    HistoryNode,
    ManualHistoryNode,
    HistoryWindow,
    WindowedHistoryNode,
    DynamicWindowedHistoryNode,
)
from promptflow.src.nodes.dummy_llm_node import DummyNode
from promptflow.src.nodes.prompt_node import PromptNode
from promptflow.src.nodes.embedding_node import (
    EmbeddingInNode,
    EmbeddingQueryNode,
    EmbeddingsIngestNode,
)
from promptflow.src.nodes.test_nodes import AssertNode, LoggingNode, InterpreterNode
from promptflow.src.nodes.env_node import EnvNode, ManualEnvNode
from promptflow.src.nodes.audio_node import WhispersNode, ElevenLabsNode
from promptflow.src.nodes.db_node import PGQueryNode, SQLiteQueryNode, PGGenerateNode
from promptflow.src.nodes.structured_data_node import JsonNode, JsonerizerNode
from promptflow.src.nodes.websearch_node import SerpApiNode, GoogleSearchNode
from promptflow.src.nodes.output_node import FileOutput, JSONFileOutput
from promptflow.src.nodes.http_node import HttpNode, JSONRequestNode, ScrapeNode
from promptflow.src.nodes.server_node import ServerInputNode
from promptflow.src.nodes.memory_node import PineconeInsertNode, PineconeQueryNode
from promptflow.src.nodes.image_node import (
    DallENode,
    CaptionNode,
    OpenImageFile,
    JSONImageFile,
    SaveImageNode,
)
from promptflow.src.connectors.connector import Connector
from promptflow.src.connectors.partial_connector import PartialConnector
from promptflow.src.state import State
from promptflow.src.text_data import TextData
from pydantic import BaseModel


class PromptFlowApp:
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


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
promptflow = PromptFlowApp()
# create the table of flowcharts if it doesn't exist
conn = sqlite3.connect("flowcharts.db")
c = conn.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS flowcharts (
    id TEXT PRIMARY KEY NOT NULL UNIQUE,
    data TEXT NOT NULL
)"""
)
conn.commit()
conn.close()


@app.get("/flowcharts")
def get_flowcharts() -> list[dict]:
    """Get all flowcharts."""
    promptflow.logger.info("Getting flowcharts")
    flowcharts = Flowchart.get_all_flowcharts(promptflow)
    return [chart.serialize() for chart in flowcharts]


@app.get("/flowcharts/{flowchart_id}")
def get_flowchart(flowchart_id: str) -> dict:
    """Get a flowchart by id."""
    promptflow.logger.info("Getting flowchart")
    try:
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id, promptflow)
    except ValueError:
        return {"message": "Flowchart not found"}
    return {"flowchart": flowchart.serialize()}


@app.post("/flowcharts/create")
def create_flowchart() -> dict:
    """Create a new flowchart."""
    promptflow.logger.info("Creating flowchart")
    flowchart = Flowchart(promptflow)
    return {"flowchart": flowchart.serialize()}


@app.post("/flowcharts/{flowchart_id}/delete")
def delete_flowchart(flowchart_id: str) -> dict:
    """
    Delete the flowchart with the given id.
    """
    promptflow.logger.info("Deleting flowchart")
    try:
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id, promptflow)
    except ValueError:
        return {"message": "Flowchart not found"}
    flowchart.delete()
    return {"message": "Flowchart deleted", "flowchart": flowchart.serialize()}


@app.get("/flowcharts/{flowchart_id}/run")
def run_flowchart(flowchart_id: str) -> dict:
    """Execute the flowchart."""
    promptflow.logger.info("Running flowchart")
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, promptflow)
    init_state = State()
    init_state = flowchart.initialize(init_state)
    final_state = flowchart.run(init_state)
    promptflow.logger.info("Finished running flowchart")
    if final_state:
        return {"state": final_state.serialize()}
    else:
        return {"state": None}


@app.get("/flowcharts/{flowchart_id}/stop")
def stop_flowchart(flowchart_id: str):
    """Stop the flowchart."""
    promptflow.logger.info("Stopping flowchart")
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, promptflow)
    flowchart.is_running = False
    flowchart.is_dirty = True
    return {"message": "Flowchart stopped", "flowchart": flowchart.serialize()}


@app.get("/flowcharts/{flowchart_id}/clear")
def clear_flowchart(flowchart_id: str):
    """Clear the flowchart."""
    promptflow.logger.info("Clearing flowchart")
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, promptflow)
    flowchart.clear()
    return {"message": "Flowchart cleared", "flowchart": flowchart.serialize()}


@app.get("/flowcharts/{flowchart_id}/cost")
def cost_flowchart(flowchart_id: str) -> dict:
    """Get the approx cost to run the flowchart"""
    promptflow.logger.info("Getting cost of flowchart")
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, promptflow)
    state = State()
    cost = flowchart.cost(state)
    return {"cost": cost}


@app.post("/flowcharts/{flowchart_id}/save_as", response_class=Response)
def save_as(flowchart_id: str) -> Response:
    """
    Serialize the flowchart and save it to a file
    """
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, promptflow)
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
            promptflow.logger.info("Saved flowchart to %s", filename)
        with open(filename, "rb") as f:
            return Response(content=f.read(), media_type="application/zip")
    else:
        promptflow.logger.info("No file selected to save to")
        return Response(status_code=404)


@app.post("/flowcharts/load_from")
def load_from(file: UploadFile = File(...)) -> dict:
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
                        embed_file = archive.extract(node["filename"], path=os.getcwd())
                        node["filename"] = embed_file
                        # load the labels
                        label_file = archive.extract(
                            node["label_file"], path=os.getcwd()
                        )
                        node["label_file"] = label_file
                flowchart = Flowchart.deserialize(data, promptflow)
                return {"flowchart": flowchart.serialize()}
    else:
        promptflow.logger.info("No file selected to load from")
        return {"message": "No file selected to load from"}


@app.post("/flowcharts/{flowchart_id}/nodes/add")
def add_node(flowchart_id: str, classname: str) -> dict:
    node_cls = eval(classname)
    if not node_cls:
        return {"message": "Node not added: invalid classname"}
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, promptflow)
    node = node_cls(flowchart, 0, 0, "New Node")
    if node:
        flowchart.add_node(node)
        return {"message": "Node added", "node": node.serialize()}
    else:
        return {"message": "Node not added: invalid classname"}


@app.post("/flowcharts/{flowchart_id}/nodes/{node_id}/remove")
def remove_node(node_id: str, flowchart_id: str) -> dict:
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, promptflow)
    node = flowchart.find_node(node_id)
    flowchart.remove_node(node)
    return {"message": "Node removed", "node": node.serialize()}


@app.post("/flowcharts/{flowchart_id}/nodes/{node_id}/connect")
def connect_nodes(flowchart_id: str, node_id: str, target_node_id: str) -> dict:
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, promptflow)
    node = flowchart.find_node(node_id)
    target_node = flowchart.find_node(target_node_id)
    if node and target_node:
        connector = Connector(node, target_node)
        flowchart.add_connector(connector)
        return {"message": "Nodes connected", "connector": connector.serialize()}
    else:
        return {"message": "Nodes not connected"}
