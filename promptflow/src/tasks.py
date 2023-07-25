import base64
import io
import logging
import traceback

import matplotlib.pyplot as plt
import networkx as nx

from promptflow.src.celery_app import celery_app
from promptflow.src.flowchart import Flowchart
from promptflow.src.postgres_interface import (
    DatabaseConfig,
    DBInterface,
    PostgresInterface,
)
from promptflow.src.state import State


def log_result_generator(interface: DBInterface, job_id: int):
    """
    Callback function to log the result of a flowchart run
    """

    def wrapper(s: str):
        interface.create_job_log(job_id, {"message": s})

    return wrapper


@celery_app.task(bind=True, name="promptflow.src.app.run_flowchart")
def run_flowchart(self, flowchart_uid: str, db_config_init: dict) -> dict:
    logging.info("Task started: run_flowchart")
    db_config = DatabaseConfig(**db_config_init)
    interface = PostgresInterface(db_config)

    try:
        logging.info("Running flowchart")
        flowchart: Flowchart = Flowchart.get_flowchart_by_uid(flowchart_uid, interface)
        if flowchart is None:
            raise ValueError(f"Flowchart with uid {flowchart_uid} not found")
        job_id = interface.create_job({"celery_id": self.request.id}, flowchart.id)
        interface.update_job_status(job_id, "PENDING")
        init_state = State()
        init_state = flowchart.initialize(
            init_state, logging_function=log_result_generator(interface, job_id)
        )
        logging.info("Flowchart initialized")

        state = init_state
        interface.update_job_status(job_id, "RUNNING")
        state = flowchart.run(
            state, logging_function=log_result_generator(interface, job_id)
        )
        interface.update_job_status(job_id, "DONE")

        logging.info("Finished running flowchart")
        logging.info("Task completed: run_flowchart")
        return {"state": state.serialize() if state is not None else None}
    except Exception as e:
        logging.error(
            f"Task failed: run_flowchart, Error: {str(traceback.format_exc())}"
        )
        raise self.retry(exc=e)


@celery_app.task(bind=True, name="promptflow.src.app.render_flowchart")
def render_flowchart(self, flowchart_uid: str, db_config_init: dict):
    logging.info("Task started: render_flowchart")
    db_config = DatabaseConfig(**db_config_init)
    interface = PostgresInterface(db_config)
    flowchart = Flowchart.get_flowchart_by_uid(flowchart_uid, interface)
    pos = flowchart.arrange_networkx(
        lambda *args, **kwargs: nx.layout.spring_layout(*args, **kwargs, seed=1337)
    )

    fig = plt.figure()
    nx.draw(flowchart.graph, pos=pos, with_labels=False)
    nx.draw_networkx_edge_labels(
        flowchart.graph, pos=pos, edge_labels=flowchart.graph.edges
    )
    nx.draw_networkx_labels(
        flowchart.graph, pos=pos, labels={node: node.label for node in flowchart.nodes}
    )

    png_image = io.BytesIO()
    plt.savefig(png_image, format="png")
    png_image.seek(0)

    # convert bytes to base64 string
    return base64.b64encode(png_image.read())
