import pytest
from fastapi.testclient import TestClient

from promptflow.src.app import app

client = TestClient(app)


@pytest.fixture
def create_test_flowchart(request):
    flowchart_type = request.param

    if flowchart_type == "simple":
        # Create a simple flowchart
        response = client.post(
            "/flowcharts",
            json={
                "flowchart": {"id": "1", "name": "test", "nodes": [], "branches": []}
            },
        )
        flowchart_id = response.json()["flowchart"]["id"]

    elif flowchart_type == "advanced":
        flowchart = {
            "flowchart": {
                "id": "1",
                "name": "test",
                "created": "2021-01-01T00:00:00.000000",
                "nodes": [
                    {
                        "id": "1",
                        "uid": "1",
                        "label": "Start",
                        "classname": "StartNode",
                        "metadata": {},
                    },
                    {
                        "id": "2",
                        "uid": "2",
                        "classname": "InitNode",
                        "label": "End",
                        "metadata": {},
                    },
                ],
                "branches": [
                    {
                        "id": "1",
                        "conditional": "True",
                        "label": "True",
                        "graph_id": "1",
                        "node1": "1",
                        "node2": "2",
                    }
                ],
            }
        }
        response = client.post("/flowcharts", json=flowchart)
        flowchart_id = response.json()["flowchart"]["id"]
    else:
        raise ValueError(f"Invalid flowchart type: {flowchart_type}")
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


@pytest.mark.parametrize("create_test_flowchart", ["simple", "advanced"], indirect=True)
def test_get_flowchart_by_id(create_test_flowchart):
    # Simulate a GET request to the /flowcharts/{flowchart_id} endpoint
    response = client.get(f"/flowcharts/{create_test_flowchart}")

    # Ensure the response is in JSON format
    assert response.headers["Content-Type"] == "application/json"

    # Ensure the response has a 200 OK status code
    assert response.status_code == 200

    # Ensure the response JSON contains the flowchart ID
    assert str(response.json()["flowchart"]["id"]) == create_test_flowchart


def test_get_flowchart_not_found():
    # Simulate a GET request to the /flowcharts/{flowchart_id} endpoint with an invalid ID
    response = client.get("/flowcharts/nonexistent")

    # Ensure the response is in JSON format
    assert response.headers["Content-Type"] == "application/json"

    # Ensure the response has a 200 OK status code
    assert response.status_code == 200

    # Ensure the response JSON contains a message indicating the flowchart was not found
    assert response.json()["message"] == "Flowchart not found"


@pytest.mark.parametrize("create_test_flowchart", ["simple", "advanced"], indirect=True)
def test_run_flowchart(create_test_flowchart):
    response = client.get(f"/flowcharts/{create_test_flowchart}/run")
    assert response.status_code == 200
    assert "started" in response.json()["message"]


@pytest.mark.parametrize("create_test_flowchart", ["simple", "advanced"], indirect=True)
def test_stop_flowchart(create_test_flowchart):
    response = client.get(f"/flowcharts/{create_test_flowchart}/stop")
    assert response.status_code == 200
    assert "Flowchart stopped" in response.json()["message"]


@pytest.mark.parametrize("create_test_flowchart", ["simple", "advanced"], indirect=True)
def test_clear_flowchart(create_test_flowchart):
    response = client.get(f"/flowcharts/{create_test_flowchart}/clear")
    assert response.status_code == 200
    assert "Flowchart cleared" in response.json()["message"]


@pytest.mark.parametrize("create_test_flowchart", ["simple", "advanced"], indirect=True)
def test_cost_flowchart(create_test_flowchart):
    response = client.get(f"/flowcharts/{create_test_flowchart}/cost")
    assert response.status_code == 200
    assert "cost" in response.json()


@pytest.mark.parametrize("create_test_flowchart", ["simple", "advanced"], indirect=True)
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


@pytest.mark.parametrize("create_test_flowchart", ["simple", "advanced"], indirect=True)
def test_add_node(create_test_flowchart):
    data = {"classname": "InputNode"}
    response = client.post(f"/flowcharts/{create_test_flowchart}/nodes", json=data)
    assert response.status_code == 200
    assert "Node added" in response.json()["message"]


@pytest.mark.parametrize("create_test_flowchart", ["simple", "advanced"], indirect=True)
def test_remove_node(create_test_flowchart):
    # First add a node
    node_data = {"classname": "InputNode"}
    add_node_response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes", json=node_data
    )
    node_id = add_node_response.json()["node"]["id"]

    # Remove the node
    response = client.delete(f"/flowcharts/{create_test_flowchart}/nodes/{node_id}")
    assert response.status_code == 200
    assert "Node removed" in response.json()["message"]


@pytest.mark.parametrize("create_test_flowchart", ["simple", "advanced"], indirect=True)
def test_connect_nodes(create_test_flowchart):
    # Add two nodes first
    node1_data = {"classname": "InputNode"}
    add_node1_response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes", json=node1_data
    )
    node1_id = add_node1_response.json()["node"]["id"]

    node2_data = {"classname": "InputNode"}
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


@pytest.mark.parametrize("create_test_flowchart", ["simple", "advanced"], indirect=True)
def test_get_node_options(create_test_flowchart):
    # Add a node first
    node_data = {"classname": "InputNode"}
    add_node_response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes", json=node_data
    )
    node_id = add_node_response.json()["node"]["id"]
    response = client.get(
        f"/flowcharts/{create_test_flowchart}/nodes/{node_id}/options"
    )
    assert response.status_code == 200
    assert "options" in response.json()


@pytest.mark.parametrize("create_test_flowchart", ["simple", "advanced"], indirect=True)
def test_update_node_options(create_test_flowchart):
    options_data = {"label": "Test label"}
    # Add a node first
    node_data = {"classname": "InputNode"}
    add_node_response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes", json=node_data
    )
    node_id = add_node_response.json()["node"]["id"]
    response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes/{node_id}/options",
        json=options_data,
    )
    assert response.status_code == 200
    assert "options updated" in response.json()["message"]


def test_get_all_jobs():
    # Simulate a GET request to the /jobs endpoint
    response = client.get("/jobs")

    # Ensure the response is in JSON format
    assert response.headers["Content-Type"] == "application/json"

    # Ensure the response has a 200 OK status code
    assert response.status_code == 200

    # Ensure the response JSON contains the jobs
    assert "jobs" in response.json()
    assert "active" in response.json()["jobs"]
    assert "scheduled" in response.json()["jobs"]
    assert "reserved" in response.json()["jobs"]


def test_get_job_by_id():
    # First, get all jobs
    all_jobs_response = client.get("/jobs")
    all_jobs = all_jobs_response.json()

    # Pick a job_id if there is any active job
    job_id = None
    job_dict = all_jobs["jobs"]["active"]
    if job_dict:
        for host, tasks in job_dict.items():
            if tasks:
                job_id = tasks[0]["request"]["id"]
                break

    if job_id:
        # Simulate a GET request to the /jobs/{job_id} endpoint
        response = client.get(f"/jobs/{job_id}")

        # Ensure the response is in JSON format
        assert response.headers["Content-Type"] == "application/json"

        # Ensure the response has a 200 OK status code
        assert response.status_code == 200

        # Ensure the response JSON contains the job
        assert "job" in response.json()
        assert response.json()["job"]["request"]["id"] == job_id
    else:
        print("No active jobs to test with")


def test_get_job_not_found():
    # Simulate a GET request to the /jobs/{job_id} endpoint with an invalid ID
    response = client.get("/jobs/nonexistent")

    # Ensure the response is in JSON format
    assert response.headers["Content-Type"] == "application/json"

    # Ensure the response has a 200 OK status code
    assert response.status_code == 200

    # Ensure the response JSON contains a message indicating the job was not found
    assert response.json()["message"] == "Job not found"
