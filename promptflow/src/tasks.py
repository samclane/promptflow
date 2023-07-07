import logging
import traceback

from promptflow.src.celery_app import celery_app
from promptflow.src.flowchart import Flowchart
from promptflow.src.postgres_interface import (
    DatabaseConfig,
    DBInterface,
    PostgresInterface,
)
from promptflow.src.state import State


@celery_app.task(bind=True, name="promptflow.src.app.run_flowchart")
def run_flowchart(self, flowchart_id: str, db_config: dict) -> dict:
    logging.info("Task started: run_flowchart")
    db_config = DatabaseConfig(**db_config)
    interface = PostgresInterface(db_config)
    job_id = interface.create_job({"celery_id": self.request.id})
    interface.update_job_status(job_id, "PENDING")

    try:
        logging.info("Running flowchart")
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id, interface)
        if flowchart is None:
            raise Exception(f"Flowchart with id {flowchart_id} not found")
        init_state = State()
        init_state = flowchart.initialize(init_state)
        logging.info("Flowchart initialized")

        state = init_state
        interface.update_job_status(job_id, "RUNNING")
        state = flowchart.run(state)
        interface.update_job_status(job_id, "DONE")

        logging.info("Finished running flowchart")
        logging.info("Task completed: run_flowchart")
        return {"state": state.serialize() if state is not None else None}
    except Exception as e:
        logging.error(
            f"Task failed: run_flowchart, Error: {str(traceback.format_exc())}"
        )
        raise self.retry(exc=e)
