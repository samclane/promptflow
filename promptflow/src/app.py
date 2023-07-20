"""
Primary application class. This class is responsible for creating the
window, menu, and canvas. It also handles the saving and loading of
flowcharts.
"""
import asyncio
import io
import json
import logging
import os
import tempfile
import traceback
import zipfile
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

import matplotlib.pyplot as plt
import networkx as nx
from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    HTTPException,
    Response,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from PIL import Image
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
        host=os.getenv("POSTGRES_HOST", "172.18.0.3"),
        database=os.getenv("POSTGRES_DB", "postgres"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        port=os.getenv("POSTGRES_PORT", 5432),
    )
)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


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
        node["node_type_id"] = interface.get_node_type_id(node["node_type"])
    return flowchart


@app.post("/flowcharts")
def upsert_flowchart_json(flowchart_json: FlowchartJson) -> dict:
    """Upsert a flowchart json file."""
    promptflow.logger.info("Upserting flowchart")
    try:
        flowchart = add_node_type_ids(flowchart_json.flowchart)
        flowchart = Flowchart.deserialize(interface, flowchart_json.flowchart)
        interface.save_flowchart(flowchart)
    except ValueError:
        return {"message": "Invalid flowchart json", "error": traceback.format_exc()}
    return flowchart.serialize()


@app.get("/flowcharts/{flowchart_id}")
def get_flowchart(flowchart_id: str) -> dict:
    """Get a flowchart by id."""
    promptflow.logger.info("Getting flowchart")
    try:
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
    except Exception as e:
        interface.conn.rollback()
        return {"message": "Flowchart not found", "error": traceback.format_exc()}
    return flowchart.serialize()


@app.delete("/flowcharts/{flowchart_id}")
def delete_flowchart(flowchart_id: str) -> dict:
    """Delete a flowchart by id."""
    promptflow.logger.info("Deleting flowchart")
    try:
        interface.delete_flowchart(flowchart_id)
    except Exception as e:
        interface.conn.rollback()
        return {"message": "Flowchart not found", "error": traceback.format_exc()}
    return {"message": "Flowchart deleted", "flowchart_id": flowchart_id}


@app.get("/flowcharts/{flowchart_id}/run")
def run_flowchart_endpoint(flowchart_id: str, background_tasks: BackgroundTasks):
    """Queue the flowchart execution as a background task."""
    task = run_flowchart.apply_async((flowchart_id, interface.config.dict()))
    return {"message": "Flowchart execution started", "task_id": str(task.id)}


@app.get("/flowcharts/{flowchart_id}/png")
def render_flowchart_png(flowchart_id: str):
    """Render a flowchart as a png."""
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
    pos = flowchart.arrange_networkx(
        lambda *args, **kwargs: nx.layout.spring_layout(*args, **kwargs, seed=1337)
    )

    fig = plt.figure()
    nx.draw(flowchart.graph, pos=pos, with_labels=True)

    png_image = io.BytesIO()
    plt.savefig(png_image, format="png")
    png_image.seek(0)

    return StreamingResponse(png_image, media_type="image/png")


@app.get("/jobs")
def get_all_jobs(graph_id: str = None, status: str = None, limit: int = None):
    """
    Get all running jobs
    """
    return interface.get_all_jobs(graph_id, status, limit)


@app.get("/jobs/{job_id}")
def get_job_by_id(job_id) -> dict:
    """Get a specific job by id"""
    try:
        return interface.get_job_view(job_id).dict()
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found")


@app.get("/jobs/{job_id}/logs")
def get_job_logs(job_id) -> dict:
    """
    Get all logs for a specific job
    """
    try:
        return {"logs": interface.get_job_logs(job_id)}
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found")


@app.websocket("/jobs/{job_id}/ws")
async def job_logs_ws(websocket: WebSocket, job_id: int):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({"logs": interface.get_job_logs(job_id)}))
        while True:
            await asyncio.sleep(1)
            await websocket.send_text(
                json.dumps({"logs": interface.get_job_logs(job_id)})
            )
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc


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
                    if node["node_type"] == "EmbeddingsIngestNode":
                        # load the embedding
                        embed_file = archive.extract(node["filename"], path=os.getcwd())
                        node["filename"] = embed_file
                        # load the labels
                        label_file = archive.extract(
                            node["label_file"], path=os.getcwd()
                        )
                        node["label_file"] = label_file
                flowchart = Flowchart.deserialize(interface, data)
                interface.save_flowchart(flowchart)
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
    node_type: str


@app.post("/flowcharts/{flowchart_id}/nodes")
def add_node(flowchart_id: str, nodetype: NodeType) -> dict:
    node_cls = node_map.get(nodetype.node_type)
    if not node_cls:
        return {"message": "Node not added: invalid node_type"}
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
    node_type_id = interface.get_node_type_id(nodetype.node_type)
    node = node_cls(flowchart, nodetype.node_type, node_type_id=node_type_id)
    if node:
        flowchart.add_node(node)
        interface.save_flowchart(flowchart)
        return {"message": "Node added", "node": node.serialize()}
    else:
        return {"message": "Node not added: invalid node_type"}


@app.delete("/flowcharts/{flowchart_id}/nodes/{node_id}")
def remove_node(node_id: str, flowchart_id: str) -> dict:
    flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
    node = flowchart.find_node(node_id)
    flowchart.remove_node(node)
    interface.save_flowchart(flowchart)
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
        interface.save_flowchart(flowchart)
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
    interface.save_flowchart(flowchart)
    return {"message": "Node options updated", "node": node.serialize()}


@app.exception_handler(HTTPException)
def handle_exception(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail)},
    )


# @app.on_event("startup")
# def startup_event():
#     loop = asyncio.new_event_loop()
#     thread = Thread(target=interface.listener, args=(manager, loop,))
#     thread.start()
