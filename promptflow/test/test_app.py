import pytest
from fastapi.testclient import TestClient

from promptflow.src.app import app

client = TestClient(app)


@pytest.fixture
def create_test_flowchart(request):
    flowchart_type = request.param

    if flowchart_type == "simple":
        # Create a simple flowchart
        flowchart = {
            "flowchart": {
                "id": "1",
                "name": "simple",
                "nodes": [
                    {
                        "id": "1",
                        "uid": "1",
                        "label": "Start",
                        "node_type": "StartNode",
                        "metadata": {},
                    },
                ],
                "branches": [],
            }
        }

    elif flowchart_type == "advanced":
        flowchart = {
            "flowchart": {
                "id": "2",
                "name": "advanced",
                "nodes": [
                    {
                        "id": "1",
                        "uid": "1",
                        "label": "Start",
                        "node_type": "StartNode",
                        "metadata": {},
                    },
                    {
                        "id": "2",
                        "uid": "2",
                        "label": "End",
                        "node_type": "InitNode",
                        "metadata": {},
                    },
                ],
                "branches": [
                    {
                        "id": "1",
                        "conditional": "",
                        "label": "True",
                        "prev": "1",
                        "next": "2",
                    }
                ],
            }
        }

    elif flowchart_type == "chat_gpt":
        flowchart = {
            "flowchart": {
                "id": "3",
                "name": "ChatGPT",
                "nodes": [
                    {
                        "id": "1",
                        "uid": "1",
                        "label": "Start",
                        "node_type": "StartNode",
                        "metadata": {},
                    },
                    {
                        "id": "2",
                        "uid": "2",
                        "label": "Initialize ChatGPT",
                        "node_type": "InitNode",
                        "metadata": {},
                    },
                    {
                        "id": "3",
                        "uid": "3",
                        "label": "Input from User",
                        "node_type": "InputNode",
                        "metadata": {},
                    },
                    {
                        "id": "4",
                        "uid": "4",
                        "label": "Process Query with ChatGPT",
                        "node_type": "OpenAINode",
                        "metadata": {},
                    },
                    {
                        "id": "5",
                        "uid": "5",
                        "label": "Output to User",
                        "node_type": "LoggingNode",
                        "metadata": {},
                    },
                ],
                "branches": [
                    {
                        "conditional": "",
                        "label": "Initialization",
                        "prev": "1",
                        "next": "2",
                    },
                    {
                        "conditional": "",
                        "label": "Receive Input",
                        "prev": "2",
                        "next": "3",
                    },
                    {
                        "conditional": "",
                        "label": "Process Input",
                        "prev": "3",
                        "next": "4",
                    },
                    {
                        "conditional": "def main(): return False",
                        "label": "Display Output",
                        "prev": "4",
                        "next": "5",
                    },
                ],
            }
        }

    else:
        raise ValueError(f"Invalid flowchart type: {flowchart_type}")
    response = client.post("/flowcharts", json=flowchart)
    if not response.status_code == 200:
        raise ValueError(
            f"Failed to create flowchart: {flowchart_type}", response.json()
        )
    flowchart_id = response.json()["id"]
    return flowchart_id


def test_get_flowcharts():
    # Simulate a GET request to the /flowcharts endpoint
    response = client.get("/flowcharts")

    # Ensure the response is in JSON format
    assert response.headers["Content-Type"] == "application/json"

    # Ensure the response has a 200 OK status code
    assert response.status_code == 200

    # Ensure the response JSON is a list
    assert isinstance(response.json(), list)


@pytest.mark.parametrize(
    "create_test_flowchart", ["simple", "advanced", "chat_gpt"], indirect=True
)
def test_get_flowchart_by_id(create_test_flowchart):
    # Simulate a GET request to the /flowcharts/{flowchart_id} endpoint
    response = client.get(f"/flowcharts/{create_test_flowchart}")

    # Ensure the response is in JSON format
    assert response.headers["Content-Type"] == "application/json"

    # Ensure the response has a 200 OK status code
    assert response.status_code == 200

    # ensure json response is a dict
    assert isinstance(response.json(), dict)

    # Ensure the response JSON contains the flowchart ID
    assert str(response.json()["id"]) == create_test_flowchart


def test_get_flowchart_not_found():
    # Simulate a GET request to the /flowcharts/{flowchart_id} endpoint with an invalid ID
    response = client.get("/flowcharts/999")

    # Ensure the response is in JSON format
    assert response.headers["Content-Type"] == "application/json"

    # Ensure the response has a 200 OK status code
    assert response.status_code == 200

    # Ensure the response JSON contains a message indicating the flowchart was not found
    assert response.json()["message"] == "Flowchart not found"


@pytest.mark.parametrize(
    "create_test_flowchart", ["simple", "advanced", "chat_gpt"], indirect=True
)
def test_run_flowchart(create_test_flowchart):
    response = client.get(f"/flowcharts/{create_test_flowchart}/run")
    assert response.status_code == 200
    assert "started" in response.json()["message"]


@pytest.mark.parametrize(
    "create_test_flowchart", ["simple", "advanced", "chat_gpt"], indirect=True
)
def test_stop_flowchart(create_test_flowchart):
    response = client.get(f"/flowcharts/{create_test_flowchart}/stop")
    assert response.status_code == 200
    assert "Flowchart stopped" in response.json()["message"]


@pytest.mark.parametrize(
    "create_test_flowchart", ["simple", "advanced", "chat_gpt"], indirect=True
)
def test_clear_flowchart(create_test_flowchart):
    response = client.get(f"/flowcharts/{create_test_flowchart}/clear")
    assert response.status_code == 200
    assert "Flowchart cleared" in response.json()["message"]


@pytest.mark.parametrize(
    "create_test_flowchart", ["simple", "advanced", "chat_gpt"], indirect=True
)
def test_cost_flowchart(create_test_flowchart):
    response = client.get(f"/flowcharts/{create_test_flowchart}/cost")
    assert response.status_code == 200
    assert "cost" in response.json()


@pytest.mark.parametrize(
    "create_test_flowchart", ["simple", "advanced", "chat_gpt"], indirect=True
)
def test_save_as(create_test_flowchart):
    response = client.post(f"/flowcharts/{create_test_flowchart}/save_as")
    assert response.status_code in [200, 404]


# def test_load_from(create_test_flowchart):
#     file_to_upload = {"file": open(create_test_flowchart, "rb")}
#     response = client.post("/flowcharts/load_from", files=file_to_upload)
#     assert response.status_code == 200


def test_get_node_types():
    response = client.get("/nodes/types")
    assert response.status_code == 200
    assert "node_types" in response.json()


@pytest.mark.parametrize(
    "create_test_flowchart", ["simple", "advanced", "chat_gpt"], indirect=True
)
def test_add_node(create_test_flowchart):
    data = {
        "node_type": "InputNode",
        "id": "1",
        "uid": "test_add_node",
        "label": "Start",
    }
    response = client.post(f"/flowcharts/{create_test_flowchart}/nodes", json=data)
    assert response.status_code == 200
    assert "Node added" in response.json()["message"]


@pytest.mark.parametrize(
    "create_test_flowchart", ["simple", "advanced", "chat_gpt"], indirect=True
)
def test_remove_node(create_test_flowchart):
    # First add a node
    node_data = {"node_type": "InputNode", "id": "1", "uid": "1", "label": "Start"}
    add_node_response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes", json=node_data
    )
    node_id = add_node_response.json()["node"]["id"]

    # Remove the node
    response = client.delete(f"/flowcharts/{create_test_flowchart}/nodes/{node_id}")
    assert response.status_code == 200
    assert "Node removed" in response.json()["message"]


@pytest.mark.parametrize(
    "create_test_flowchart", ["simple", "advanced", "chat_gpt"], indirect=True
)
def test_connect_nodes(create_test_flowchart):
    # Add two nodes first
    node1_data = {"node_type": "InputNode"}
    add_node1_response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes", json=node1_data
    )
    node1_id = add_node1_response.json()["node"]["id"]

    node2_data = {"node_type": "InputNode"}
    add_node2_response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes", json=node2_data
    )
    node2_id = add_node2_response.json()["node"]["id"]

    # Connect the nodes
    connection_data = {"target_node_id": node2_id}
    response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes/{node1_id}/connect",
        json=connection_data,
    )
    assert response.status_code == 200
    assert "Nodes connected" in response.json()["message"]


@pytest.mark.parametrize(
    "create_test_flowchart", ["simple", "advanced", "chat_gpt"], indirect=True
)
def test_get_node_options(create_test_flowchart):
    # Add a node first
    node_data = {"node_type": "InputNode", "id": "1", "uid": "1", "label": "Start"}
    add_node_response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes", json=node_data
    )
    node_id = add_node_response.json()["node"]["id"]
    response = client.get(
        f"/flowcharts/{create_test_flowchart}/nodes/{node_id}/options"
    )
    assert response.status_code == 200
    assert "options" in response.json()


def test_get_jobs():
    # call the /jobs endpoint
    response = client.get("/jobs")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_job_by_id():
    # call the /jobs/{id} endpoint
    response = client.get("/jobs/1")
    assert response.status_code == 200


def test_get_job_not_found():
    # call the /jobs/{id} endpoint
    response = client.get("/jobs/999")
    assert response.status_code == 404


def test_get_job_logs():
    response = client.get("/jobs/1/logs")
    assert response.status_code == 200
    assert "logs" in response.json()
