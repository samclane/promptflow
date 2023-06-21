from promptflow.src.celery_app import celery_app
from promptflow.src.flowchart import Flowchart
from promptflow.src.state import State
import logging


@celery_app.task(bind=True, name="promptflow.src.app.run_flowchart")
def run_flowchart(self, flowchart_id: str) -> dict:
    logging.info("Task started: run_flowchart")

    try:
        logging.info("Running flowchart")
        flowchart = Flowchart.get_flowchart_by_id(flowchart_id)
        if flowchart is None:
            raise Exception(f"Flowchart with id {flowchart_id} not found")
        init_state = State()
        init_state = flowchart.initialize(init_state)
        logging.info("Flowchart initialized")

        state = init_state
        flowchart.run(state)

        logging.info("Finished running flowchart")
        logging.info("Task completed: run_flowchart")
        return {"state": "COMPLETED"}
    except Exception as e:
        logging.error(f"Task failed: run_flowchart, Error: {str(e)}")
        raise self.retry(exc=e)
