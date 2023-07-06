"""
Test all nodes in the node_map
"""
import pytest
from fastapi.testclient import TestClient

from promptflow.src.app import app
from promptflow.src.node_map import node_map

client = TestClient(app)


# create a pytest fixture to test all nodes in the node_map
@pytest.fixture
def node(request):
    return request.param


@pytest.fixture
def create_test_flowchart():
    response = client.post(
        "/flowcharts",
        json={"flowchart": {"id": "1", "name": "test", "nodes": [], "connectors": []}},
    )
    flowchart_id = response.json()["flowchart"]["id"]
    return flowchart_id


@pytest.mark.parametrize("node", node_map.values())
def test_add_node(node, create_test_flowchart):
    response = client.post(
        f"/flowcharts/{create_test_flowchart}/nodes",
        json={"classname": node.__name__, "label": "test"},
    )
    assert response.status_code == 200
    assert response.json()["node"]["label"] == node.__name__
