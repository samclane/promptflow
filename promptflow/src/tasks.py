import base64
import io
import logging
import traceback

import matplotlib.pyplot as plt
import networkx as nx

from promptflow.src.celery_app import celery_app
from promptflow.src.flowchart import Flowchart
from promptflow.src.nodes.node_base import NxNodeShape
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
        if not flowchart.id:
            raise ValueError(
                f"Flowchart with uid {flowchart_uid} has not been saved to the database"
            )
        job_id = interface.create_job({"celery_id": self.request.id}, flowchart.id)
        interface.update_job_status(job_id, "PENDING")
        init_state = flowchart.initialize(
            job_id,
            State(),
            interface,
            logging_function=log_result_generator(interface, job_id),
        )
        logging.info("Flowchart initialized")

        state = init_state
        interface.update_job_status(job_id, "RUNNING")
        state = flowchart.run(
            job_id,
            state,
            interface,
            logging_function=log_result_generator(interface, job_id),
        )
        interface.update_job_status(job_id, "DONE")
        if state is not None:
            interface.insert_job_output(job_id, "JSON", str(state.serialize()))
        else:
            interface.insert_job_output(job_id, "JSON", str({}))

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
    plt.box(False)
    plt.margins(0.2)
    node_size = max(list(map(lambda x: len(x.label) * 350, flowchart.nodes)))
    for shape in NxNodeShape:
        nodes = filter(lambda x: x.nx_shape == shape, flowchart.nodes)
        nx.draw_networkx_nodes(
            flowchart.graph.subgraph(nodes),
            pos=pos,
            nx_shape=shape.value,
            node_color=list(map(lambda x: x.node_color, nodes)),
            node_size=node_size,
        )
    nx.draw_networkx_edges(
        flowchart.graph,
        pos=pos,
        edgelist=flowchart.graph.edges,
        node_size=node_size,
    )
    nx.draw_networkx_edge_labels(
        flowchart.graph,
        pos=pos,
        edge_labels={
            e: c.label for e, c in zip(flowchart.graph.edges, flowchart.connectors)
        },
        rotate=False,
        bbox=dict(
            boxstyle="round", pad=0.2, facecolor="white", edgecolor="none", alpha=1
        ),
    )

    nx.draw_networkx_labels(
        flowchart.graph,
        pos=pos,
        labels={node: node.label for node in flowchart.nodes},
        font_size=10,
    )

    plt.tight_layout()

    png_image = io.BytesIO()
    plt.savefig(png_image, format="png", dpi=300, bbox_inches="tight")
    png_image.seek(0)

    # convert bytes to base64 string
    return base64.b64encode(png_image.read())
