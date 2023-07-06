"""
Primary application class. This class is responsible for creating the
window, menu, and canvas. It also handles the saving and loading of
flowcharts.
"""
import json
import logging
import os
import zipfile

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from promptflow.src.celery_app import celery_app
from promptflow.src.connectors.connector import Connector
from promptflow.src.flowchart import Flowchart
from promptflow.src.node_map import node_map
from promptflow.src.nodes.embedding_node import EmbeddingsIngestNode
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.postgres_interface import DatabaseConfig, PostgresInterface
from promptflow.src.state import State
from promptflow.src.tasks import run_flowchart


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

interface = PostgresInterface(
    DatabaseConfig(
        host="172.18.0.3",
        database="postgres",
        user="postgres",
        password="postgres",
    )
)


@app.get("/flowcharts")
def get_flowcharts() -> list[dict]:
    """Get all flowcharts."""
    promptflow.logger.info("Getting flowcharts")
    flowcharts = interface.get_all_flowchart_ids_and_names()
    return flowcharts


class FlowchartJson(BaseModel):
    """A flowchart json file"""

    flowchart: dict


def add_node_type_ids(flowchart: dict):
    """Add node type ids to the flowchart"""
    for node in flowchart["nodes"]:
        node["node_type_id"] = interface.get_node_type_id(node["classname"])
    return flowchart


@app.post("/flowcharts")
def upsert_flowchart_json(flowchart_json: FlowchartJson) -> dict:
    """Upsert a flowchart json file."""
    promptflow.logger.info("Upserting flowchart")
    try:
        flowchart = add_node_type_ids(flowchart_json.flowchart)
        flowchart = Flowchart.deserialize(interface, flowchart_json.flowchart)
    except ValueError:
        return {"message": "Invalid flowchart json file"}
    return {"flowchart": flowchart.serialize()}


@app.get("/flowcharts/{flowchart_id}")
def get_flowchart(flowchart_id: str) -> dict:
    """Get a flowchart by id."""
    promptflow.logger.info("Getting flowchart")
    try:
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
    except Exception as e:
        interface.conn.rollback()
        return {"message": "Flowchart not found", "error": str(e)}
    return {"flowchart": flowchart.serialize()}


@app.get("/flowcharts/{flowchart_id}/run")
def run_flowchart_endpoint(flowchart_id: str, background_tasks: BackgroundTasks):
    """Queue the flowchart execution as a background task."""
    task = run_flowchart.apply_async((flowchart_id, interface.config.dict()))
    return {"message": "Flowchart execution started", "task_id": str(task.id)}


@app.get("/jobs")
def get_all_jobs():
    """Get all running celery jobs by querying the celery backend"""
    jobs = celery_app.control.inspect()
    jobs = {
        "active": jobs.active(),
        "scheduled": jobs.scheduled(),
        "reserved": jobs.reserved(),
    }
    return {"jobs": jobs}


@app.get("/jobs/{job_id}")
def get_job_by_id(job_id) -> dict:
    """Get a celery job by id"""
    jobs = celery_app.control.inspect()
    for job_type in ["active", "scheduled", "reserved"]:
        job_dict = getattr(jobs, job_type)()
        for host, tasks in job_dict.items() if job_dict else {}:
            for job in tasks:
                if job["request"]["id"] == job_id:
                    return {"job": job}
    return {"message": "Job not found"}


@app.get("/flowcharts/{flowchart_id}/stop")
def stop_flowchart(flowchart_id: str):
    """Stop the flowchart."""
    promptflow.logger.info("Stopping flowchart")
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
    flowchart.is_running = False
    flowchart.is_dirty = True
    return {"message": "Flowchart stopped", "flowchart": flowchart.serialize()}


@app.get("/flowcharts/{flowchart_id}/clear")
def clear_flowchart(flowchart_id: str):
    """Clear the flowchart."""
    promptflow.logger.info("Clearing flowchart")
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
    flowchart.clear()
    return {"message": "Flowchart cleared", "flowchart": flowchart.serialize()}


@app.get("/flowcharts/{flowchart_id}/cost")
def cost_flowchart(flowchart_id: str) -> dict:
    """Get the approx cost to run the flowchart"""
    promptflow.logger.info("Getting cost of flowchart")
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
    state = State()
    cost = flowchart.cost(state)
    return {"cost": cost}


@app.post("/flowcharts/{flowchart_id}/save_as", response_class=Response)
def save_as(flowchart_id: str) -> Response:
    """
    Serialize the flowchart and save it to a file
    """
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
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
                flowchart = Flowchart.deserialize(interface, data)
                return {"flowchart": flowchart.serialize()}
    else:
        promptflow.logger.info("No file selected to load from")
        return {"message": "No file selected to load from"}


@app.get("/nodes/types")
def get_node_types() -> dict:
    """Get all node types."""
    node_types = NodeBase.get_all_node_types()
    return {"node_types": node_types}


# Force FastAPI to accept a JSON body for the node type
class NodeType(BaseModel):
    classname: str


@app.post("/flowcharts/{flowchart_id}/nodes")
def add_node(flowchart_id: str, nodetype: NodeType) -> dict:
    node_cls = node_map.get(nodetype.classname)
    if not node_cls:
        return {"message": "Node not added: invalid classname"}
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
    node_type_id = interface.get_node_type_id(nodetype.classname)
    node = node_cls(flowchart, nodetype.classname, node_type_id=node_type_id)
    if node:
        flowchart.add_node(node)
        return {"message": "Node added", "node": node.serialize()}
    else:
        return {"message": "Node not added: invalid classname"}


@app.delete("/flowcharts/{flowchart_id}/nodes/{node_id}")
def remove_node(node_id: str, flowchart_id: str) -> dict:
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
    node = flowchart.find_node(node_id)
    flowchart.remove_node(node)
    return {"message": "Node removed", "node": node.serialize()}


class NodeData(BaseModel):
    target_node_id: str


@app.post("/flowcharts/{flowchart_id}/nodes/{node_id}/connect")
def connect_nodes(flowchart_id: str, node_id: str, target_node_id: NodeData) -> dict:
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
    node = flowchart.find_node(node_id)
    target_node = flowchart.find_node(target_node_id.target_node_id)
    if node and target_node:
        connector = Connector(node, target_node)
        flowchart.add_connector(connector)
        return {"message": "Nodes connected", "connector": connector.serialize()}
    else:
        return {"message": "Nodes not connected"}


@app.get("/flowcharts/{flowchart_id}/nodes/{node_id}/options")
def get_node_options(flowchart_id: str, node_id: str) -> dict:
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
    node = flowchart.find_node(node_id)
    options = node.get_options()
    return {"options": options}


@app.post("/flowcharts/{flowchart_id}/nodes/{node_id}/options")
def update_node_options(flowchart_id: str, node_id: str, data: dict) -> dict:
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
    node = flowchart.find_node(node_id)
    node.update(data)
    return {"message": "Node options updated", "node": node.serialize()}


@app.exception_handler(HTTPException)
def handle_exception(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail)},
    )
