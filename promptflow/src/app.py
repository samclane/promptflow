"""
Primary application class. This class is responsible for creating the
window, menu, and canvas. It also handles the saving and loading of
flowcharts.
"""

import datetime
import sys

import redis

from promptflow.src import chatbot

sys.path.append("./")

import dotenv

dotenv.load_dotenv()

import io
import json
import logging
import os
import traceback
import zipfile
from typing import Any, List, Optional

from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from promptflow.src.celery_app import celery_app
from promptflow.src.flowchart import Flowchart, FlowchartJson
from promptflow.src.node_map import node_map
from promptflow.src.nodes.embedding_node import EmbeddingsIngestNode
from promptflow.src.postgres_interface import (
    DatabaseConfig,
    GraphNamesAndIds,
    JobLog,
    JobResult,
    JobView,
    PostgresInterface,
)
from promptflow.src.state import State
from promptflow.src.tasks import render_flowchart, run_flowchart


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
        host=os.getenv("POSTGRES_HOST", "172.21.0.2"),
        database=os.getenv("POSTGRES_DB", "postgres"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
    )
)


@app.get("/flowcharts")
def get_flowcharts() -> List[GraphNamesAndIds]:
    """Get all flowcharts."""
    promptflow.logger.info("Getting flowcharts")
    flowcharts = interface.get_all_flowchart_ids_and_names()
    return flowcharts


class ErrorResponse(BaseModel):
    """A response for an error"""

    message: str
    error: str
    data: Optional[dict]


def add_node_type_ids(flowchart: dict) -> dict[str, Any]:
    """Add node type ids to the flowchart"""
    for node in flowchart["nodes"]:
        node["node_type_id"] = interface.get_node_type_id(node["node_type"])
    return flowchart


@app.post("/flowcharts")
def upsert_flowchart_json(
    flowchart_json: FlowchartJson,
) -> FlowchartJson | ErrorResponse:
    """Upsert a flowchart json file."""
    promptflow.logger.info("Upserting flowchart")
    try:
        data = add_node_type_ids(flowchart_json.dict())
        flowchart = Flowchart.deserialize(interface, data)
        interface.save_flowchart(flowchart)
    except ValueError:
        return ErrorResponse(
            message="Invalid flowchart json",
            error=traceback.format_exc(),
            data=flowchart_json.dict(),
        )
    return flowchart.serialize()


@app.get("/flowcharts/{flowchart_id}")
def get_flowchart(flowchart_id: str) -> FlowchartJson | ErrorResponse:
    """Get a flowchart by id."""
    promptflow.logger.info("Getting flowchart")
    try:
        flowchart = Flowchart.get_flowchart_by_uid(flowchart_id, interface)
    except ValueError:
        interface.conn.rollback()
        return ErrorResponse(
            message="Flowchart not found",
            error=traceback.format_exc(),
            data={"flowchart_id": flowchart_id},
        )
    return flowchart.serialize()


class FlowchartUpdate(BaseModel):
    """A flowchart update"""

    message: str
    flowchart_id: str


@app.delete("/flowcharts/{flowchart_id}")
def delete_flowchart(flowchart_id: str) -> FlowchartUpdate | ErrorResponse:
    """Delete a flowchart by id."""
    promptflow.logger.info("Deleting flowchart")
    try:
        interface.delete_flowchart(flowchart_id)
    except ValueError:
        interface.conn.rollback()
        return ErrorResponse(
            message="Flowchart not found",
            error=traceback.format_exc(),
            data={"flowchart_id": flowchart_id},
        )
    return FlowchartUpdate(message="Flowchart deleted", flowchart_id=flowchart_id)


class RunSuccessResponse(BaseModel):
    """A response for a successful run"""

    message: str
    task_id: str


@app.get("/flowcharts/{flowchart_uid}/run")
def run_flowchart_endpoint(flowchart_uid: str) -> RunSuccessResponse:
    """Queue the flowchart execution as a background task."""
    task = run_flowchart.apply_async((flowchart_uid, interface.config.dict()))
    return RunSuccessResponse(
        message="Flowchart execution started", task_id=str(task.id)
    )


class UserInput(BaseModel):
    """Wrapper for user input"""

    input: str


class UserInputResponse(BaseModel):
    """A response for a user input"""

    message: str
    input: str


@app.post("/jobs/{task_id}/input")
def post_input(task_id: str, user_input: UserInput) -> UserInputResponse:
    """Post input to a running flowchart execution."""
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise HTTPException(status_code=500, detail="Redis URL not found")
    red = redis.StrictRedis.from_url(redis_url)
    red.publish(f"{task_id}/input", user_input.input)
    return UserInputResponse(message="Input received", input=user_input.input)


class FileInputResponse(BaseModel):
    """A response for a file input"""

    file: str


@app.post("/jobs/{task_id}/file_input")
def post_file_input(task_id: str, file: UploadFile = File(...)) -> FileInputResponse:
    """Post input to a running flowchart execution."""
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise HTTPException(status_code=500, detail="Redis URL not found")
    red = redis.StrictRedis.from_url(redis_url)
    red.publish(f"{task_id}/input", file.file.read())
    if not file.filename:
        raise HTTPException(status_code=500, detail="File name not found")
    return FileInputResponse(file=file.filename)


@app.get("/jobs/{job_id}/output")
def get_output(job_id: int) -> JobResult:
    """Get output from a running flowchart execution."""
    return interface.get_job_output(job_id)


@app.get("/flowcharts/{flowchart_id}/png")
def render_flowchart_png(flowchart_id: str) -> StreamingResponse:
    """Render a flowchart as a png."""
    png_image = render_flowchart.apply_async(
        (flowchart_id, interface.config.dict())
    ).get()
    interface.store_b64_image(png_image, flowchart_id)
    return StreamingResponse(io.BytesIO(png_image), media_type="image/png")


class FlowchartJSResponse(BaseModel):
    """A response for a flowchart.js representation of a flowchart"""

    flowchart_js: str
    color_map: dict[str, str]


@app.get("/flowcharts/{flowchart_id}/flowchartjs")
def get_flowchart_js(flowchart_id: str) -> FlowchartJSResponse:
    """
    Returns a flowchart.js representation of the flowchart
    """
    flowchart = Flowchart.get_flowchart_by_uid(flowchart_id, interface)
    fc_js = flowchart.to_flowchart_js()
    color_map = flowchart.get_color_map()
    return FlowchartJSResponse(flowchart_js=fc_js, color_map=color_map)


@app.get("/flowcharts/{flowchart_id}/mermaid", response_class=PlainTextResponse)
def get_flowchart_mermaid(flowchart_id: str) -> str:
    """
    Returns a mermaid representation of the flowchart
    """
    flowchart = Flowchart.get_flowchart_by_uid(flowchart_id, interface)
    return flowchart.to_mermaid()


@app.get("/jobs")
def get_all_jobs(
    graph_uid: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[JobView]:
    """
    Get all running jobs
    """
    return interface.get_all_jobs(graph_uid, status, limit)


@app.get("/jobs/{job_id}")
def get_job_by_id(job_id) -> JobView:
    """Get a specific job by id"""
    try:
        return interface.get_job_view(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc


@app.get("/jobs/{job_id}/logs")
def get_job_logs(job_id) -> List[JobLog]:
    """
    Get all logs for a specific job
    """
    try:
        return interface.get_job_logs(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc


class FlowchartUpdateResponse(BaseModel):
    """A response for a flowchart update"""

    message: str
    flowchart: FlowchartJson


@app.get("/flowcharts/{flowchart_id}/stop")
def stop_flowchart(flowchart_id: str) -> FlowchartUpdateResponse:
    """Stop the flowchart."""
    promptflow.logger.info("Stopping flowchart")
    flowchart = Flowchart.get_flowchart_by_uid(flowchart_id, interface)
    for job in interface.get_all_jobs(flowchart_id):
        if not job.metadata or "celery_id" not in job.metadata:
            raise HTTPException(
                status_code=500,
                detail="Celery ID not found for job",
            )
        # actually terminate the job in celery
        celery_app.control.revoke(job.metadata["celery_id"], terminate=True)
        interface.update_job_status(job.job_id, "DONE")
    return FlowchartUpdateResponse(
        message="Flowchart stopped", flowchart=flowchart.serialize()
    )


@app.get("/flowcharts/{flowchart_id}/clear")
def clear_flowchart(flowchart_id: str) -> FlowchartUpdateResponse:
    """Clear the flowchart."""
    promptflow.logger.info("Clearing flowchart")
    flowchart = Flowchart.get_flowchart_by_uid(flowchart_id, interface)
    flowchart.clear()
    return FlowchartUpdateResponse(
        message="Flowchart cleared", flowchart=flowchart.serialize()
    )


class CostResponse(BaseModel):
    """A response for a flowchart cost"""

    flowchart_id: str
    cost: float


@app.get("/flowcharts/{flowchart_id}/cost")
def cost_flowchart(flowchart_id: str) -> CostResponse:
    """Get the approx cost to run the flowchart"""
    promptflow.logger.info("Getting cost of flowchart")
    flowchart = Flowchart.get_flowchart_by_uid(flowchart_id, interface)
    state = State()
    cost = flowchart.cost(state)
    return CostResponse(flowchart_id=flowchart_id, cost=cost)


@app.post("/flowcharts/{flowchart_id}/save_as", response_class=Response)
def save_as(flowchart_id: str) -> Response:
    """
    Serialize the flowchart and save it to a file
    """
    flowchart = Flowchart.get_flowchart_by_uid(flowchart_id, interface)
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
def load_from(file: UploadFile = File(...)) -> FlowchartJson | ErrorResponse:
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
                return flowchart.serialize()
    else:
        promptflow.logger.info("No file selected to load from")
        # return {"message": "No file selected to load from"}
        return ErrorResponse(
            message="No file selected to load from",
            error="No file selected to load from",
            data={},
        )


class NodeTypeInfoResponse(BaseModel):
    """A response for a node type info"""

    name: str
    description: str
    options: List[str]


class NodeTypesResponse(BaseModel):
    """A response for a node type"""

    node_types: List[NodeTypeInfoResponse]


@app.get("/nodes/types")
def get_node_types() -> NodeTypesResponse:
    """Get all node types."""
    return NodeTypesResponse(
        node_types=[
            NodeTypeInfoResponse(
                name=subclass.__name__,
                description=subclass.description(),
                options=subclass.get_option_keys(),
            )
            for subclass in node_map.values()
        ]
    )


@app.get("/nodes/{node_type}")
def get_node_type_info(node_type: str) -> NodeTypeInfoResponse:
    """Get the description and options for a node."""
    subclass = node_map[node_type]
    return NodeTypeInfoResponse(
        name=subclass.__name__,
        description=subclass.description(),
        options=subclass.get_option_keys(),
    )


class NodeOptionsResponse(BaseModel):
    """A response for a node options"""

    options: dict


@app.get("/flowcharts/{flowchart_id}/nodes/{node_id}/options")
def get_specific_node_options(flowchart_id: str, node_id: str) -> NodeOptionsResponse:
    """Get the editable options for a node."""
    flowchart = Flowchart.get_flowchart_by_uid(flowchart_id, interface)
    node = flowchart.find_node(node_id)
    options = node.get_options()
    return NodeOptionsResponse(options=options)


class NodeUpdateResponse(BaseModel):
    """A response for a node update"""

    node: dict
    message: str


@app.post("/flowcharts/{flowchart_id}/nodes/{node_id}/options")
def update_node_options(
    flowchart_id: str, node_id: str, data: dict
) -> NodeUpdateResponse:
    """Update the editable options for a node."""
    flowchart = Flowchart.get_flowchart_by_uid(flowchart_id, interface)
    node = flowchart.find_node(node_id)
    node.update(data)
    interface.save_flowchart(flowchart)
    return NodeUpdateResponse(message="Node options updated", node=node.serialize())


@app.post("/chat")
def post_message(
    messages: List[chatbot.ChatMessage],
    options: Optional[chatbot.ChatbotOptions] = None,
) -> chatbot.ChatResponse:
    """Post a message to the chatbot"""
    bot = chatbot.Chatbot()
    ai_response = bot.chat(messages, options)
    return chatbot.ChatResponse(
        user_message=messages[-1],
        ai_message=chatbot.ChatMessage(
            text=ai_response,
            sender="AI",
            timestamp=datetime.datetime.now().strftime("%H:%M:%S"),
        ),
    )


@app.exception_handler(HTTPException)
def handle_exception(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail)},
    )
