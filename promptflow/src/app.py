"""
Primary application class. This class is responsible for creating the
window, menu, and canvas. It also handles the saving and loading of
flowcharts.
"""
import json
import logging
from fastapi import FastAPI, Response, File, UploadFile
import os
import zipfile
from promptflow.src.flowchart import Flowchart

from promptflow.src.nodes.embedding_node import (
    EmbeddingsIngestNode,
)
from promptflow.src.state import State

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
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id, self)
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
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id, self)
        flowchart.is_running = False
        flowchart.is_dirty = True
        return {"message": "Flowchart stopped"}

    @app.get("/flowcharts/{flowchart_id}/serialize")
    def serialize_flowchart(self, flowchart_id: int) -> dict:
        """Serialize the flowchart to JSON."""
        self.logger.info("Serializing flowchart")
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id, self)
        chart_json = json.dumps(flowchart.serialize(), indent=4)
        self.logger.info(chart_json)
        return {"flowchart": chart_json}

    @app.get("/flowcharts/{flowchart_id}/clear")
    def clear_flowchart(self, flowchart_id: int):
        """Clear the flowchart."""
        self.logger.info("Clearing flowchart")
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id, self)
        flowchart.clear()
        return {"message": "Flowchart cleared"}

    @app.get("/flowcharts/{flowchart_id}/cost")
    def cost_flowchart(self, flowchart_id: int) -> dict:
        """Get the approx cost to run the flowchart"""
        self.logger.info("Getting cost of flowchart")
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id, self)
        state = State()
        cost = flowchart.cost(state)
        return {"cost": cost}

    @app.post("/flowcharts/{flowchart_id}/save_as")
    def save_as(self, flowchart_id: int) -> dict | Response:
        """
        Serialize the flowchart and save it to a file
        """
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id, self)
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
                    flowchart = Flowchart.deserialize(data, self)
                    return {"flowchart": flowchart.serialize()}
        else:
            self.logger.info("No file selected to load from")
            return {"message": "No file selected to load from"}

    @app.post("/nodes/{classname}/add")
    def add_node(self, classname: str, flowchart_id: int) -> dict:
        node = exec(f"{classname}()")
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id, self)
        if node:
            flowchart.add_node(node)
            return {"message": "Node added"}
        else:
            return {"message": "Node not added: invalid classname"}

    @app.post("/nodes/{node_id}/remove")
    def remove_node(self, node_id: str, flowchart_id: int) -> dict:
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id, self)
        node = flowchart.find_node(node_id)
        flowchart.remove_node(node)
        return {"message": "Node removed"}
