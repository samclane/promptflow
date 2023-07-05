import json
from fastapi.testclient import TestClient
import pytest
import shutil
import os

from promptflow.src.app import app

client = TestClient(app)


@pytest.fixture
def create_test_flowchart():
    # Create a flowchart using the create endpoint
    response = client.post("/flowcharts/create")
    flowchart_id = response.json()["flowchart"]["id"]
    return flowchart_id


def test_get_flowcharts(create_test_flowchart):
    # Simulate a GET request to the /flowcharts endpoint
    response = client.get("/flowcharts")

    # Ensure the response is in JSON format
    assert response.headers["Content-Type"] == "application/json"

    # Ensure the response has a 200 OK status code
    assert response.status_code == 200

    # Ensure the response JSON is a list
    assert isinstance(response.json(), list)


def test_get_flowchart_not_found(create_test_flowchart):
    # Simulate a GET request to the /flowcharts/{flowchart_id} endpoint with an invalid ID
    response = client.get("/flowcharts/nonexistent")

    # Ensure the response is in JSON format
    assert response.headers["Content-Type"] == "application/json"

    # Ensure the response has a 200 OK status code
    assert response.status_code == 200

    # Ensure the response JSON contains a message indicating the flowchart was not found
    assert response.json()["message"] == "Flowchart not found"


def test_run_flowchart(create_test_flowchart):
    response = client.get(f"/flowcharts/{create_test_flowchart}/run")
    assert response.status_code == 200
    assert "started" in response.json()["message"]


def test_stop_flowchart(create_test_flowchart):
    response = client.get(f"/flowcharts/{create_test_flowchart}/stop")
    assert response.status_code == 200
    assert "Flowchart stopped" in response.json()["message"]


def test_clear_flowchart(create_test_flowchart):
    response = client.get(f"/flowcharts/{create_test_flowchart}/clear")
    assert response.status_code == 200
    assert "Flowchart cleared" in response.json()["message"]


def test_cost_flowchart(create_test_flowchart):
    response = client.get(f"/flowcharts/{create_test_flowchart}/cost")
    assert response.status_code == 200
    assert "cost" in response.json()


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


def test_add_node(create_test_flowchart):
    data = {"classname": "InputNode"}
    response = client.post(f"/flowcharts/{create_test_flowchart}/nodes/add", json=data)
    assert response.status_code == 200
    assert "Node added" in response.json()["message"]


def test_remove_node(create_test_flowchart):
    # First add a node
    node_data = {"classname": "InputNode"}
    add_node_response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes/add", json=node_data
    )
    node_id = add_node_response.json()["node"]["id"]

    # Remove the node
    response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes/{node_id}/remove"
    )
    assert response.status_code == 200
    assert "Node removed" in response.json()["message"]


def test_connect_nodes(create_test_flowchart):
    # Add two nodes first
    node1_data = {"classname": "InputNode"}
    add_node1_response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes/add", json=node1_data
    )
    node1_id = add_node1_response.json()["node"]["id"]

    node2_data = {"classname": "InputNode"}
    add_node2_response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes/add", json=node2_data
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


def test_get_node_options(create_test_flowchart):
    # Add a node first
    node_data = {"classname": "InputNode"}
    add_node_response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes/add", json=node_data
    )
    node_id = add_node_response.json()["node"]["id"]
    response = client.get(
        f"/flowcharts/{create_test_flowchart}/nodes/{node_id}/options"
    )
    assert response.status_code == 200
    assert "options" in response.json()


def test_update_node_options(create_test_flowchart):
    options_data = {"label": "Test label"}
    # Add a node first
    node_data = {"classname": "InputNode"}
    add_node_response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes/add", json=node_data
    )
    node_id = add_node_response.json()["node"]["id"]
    response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes/{node_id}/options",
        json=options_data,
    )
    assert response.status_code == 200
    assert "options updated" in response.json()["message"]
