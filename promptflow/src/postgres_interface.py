from pydantic import BaseModel, validator, constr, conint, ValidationError
from datetime import datetime
from typing import Optional, Dict, Any, List
import psycopg2

from promptflow.src.flowchart import Flowchart
from promptflow.src.node_map import node_map


class GraphView(BaseModel):
    graph_id: conint(gt=0)
    created: datetime
    graph_name: constr(min_length=1)
    node_label: constr(min_length=1)
    node_type_metadata: Optional[Dict[str, Any]]
    node_type_name: constr(min_length=1)
    next_node: Optional[conint(gt=0)]
    current_node: conint(gt=0)
    conditional: Optional[str]
    has_conditional: bool

    @validator("created")
    def validate_created(cls, value):
        if value > datetime.now():
            raise ValueError("created must be in the past")
        return value

    @validator("node_type_metadata")
    def validate_node_type_metadata(cls, value):
        if value is not None:
            if not isinstance(value, dict):
                raise TypeError("node_type_metadata must be a dictionary")
        return value

    @validator("has_conditional")
    def validate_has_conditional(cls, value, values):
        if value and "conditional" not in values:
            raise ValueError("conditional must be provided if has_conditional is True")
        return value


class DatabaseConfig(BaseModel):
    host: str
    database: str
    user: str
    password: str

    @validator("host")
    def validate_host(cls, value):
        if not value:
            raise ValueError("host must be a non-empty string")
        return value

    @validator("database")
    def validate_database(cls, value):
        if not value:
            raise ValueError("database must be a non-empty string")
        return value

    @validator("user")
    def validate_user(cls, value):
        if not value:
            raise ValueError("user must be a non-empty string")
        return value

    @validator("password")
    def validate_password(cls, value):
        if not value:
            raise ValueError("password must be a non-empty string")
        return value


class GraphNamesAndIds(BaseModel):
    id: int
    name: str

    def hydrate(row: Dict[str, Any]):
        return GraphNamesAndIds(row["id"], row.get("name"))


def row_results_to_class_list(class_name, list_of_rows):
    return [class_name.hydrate(dict(zip(row))) for row in list_of_rows]


def row_results_to_class(class_name, list_of_rows):
    return row_results_to_class_list(class_name, list_of_rows)[0]


class PostgresInterface:
    def __init__(self, config: DatabaseConfig):
        self.conn = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password,
        )
        self.cursor = self.conn.cursor()

    def get_graph_names_and_ids(
        self,
    ) -> List[GraphNamesAndIds]:  # todo deprecate this method
        self.cursor.execute(
            "SELECT graph_id as id, name FROM graph_view"
        )  # todo select id,name from graph_view  for function get_graph_view
        # todo for function get_graph_view_to_flowchart_list select id,name from graph_view where id = input_id
        rows = self.cursor.fetchall()
        return row_results_to_class_list(GraphNamesAndIds, rows)

        """
        # Getting column names
        column_names = [desc[0] for desc in self.cursor.description]

        # Parsing and validating the rows using the GraphView model
        graph_views = []
        for row in rows:
            # Creating a dictionary from row data
            row_data = dict(zip(column_names, row))
            try:
                # Parsing the row data through the GraphView model
                graph_view = GraphView(**row_data)
                graph_views.append(graph_view)
            except ValidationError as e:
                print(f"Validation error for row {row}: {e}")

        return graph_views
        """

    def build_flowchart_from_graph_view(
        self, graph_view: List[GraphView]
    ) -> List[Flowchart]:
        flowcharts: List[Flowchart] = []
        for row in graph_view:
            if row.graph_id not in [x.id for x in flowcharts]:
                flowchart = Flowchart(False, row.graph_id, row.graph_name, row.created)
                flowcharts.append(flowchart)
            else:
                # Find the flowchart with the same graph_id
                flowchart = next((x for x in flowcharts if x.id == row.graph_id), None)
                if flowchart is None:
                    raise ValueError(
                        f"Flowchart with graph_id {row.graph_id} not found"
                    )
            node_cls = node_map.get(row.node_type_name)
            if node_cls is None:
                raise ValueError(
                    f"Node type {row.node_type_name} not found in node_map"
                )
            node = node_cls.deserialize(
                flowchart,
                (row.node_type_metadata or {})
                | {
                    "label": row.node_label,
                    "center_x": 0,
                    "center_y": 0,
                },  # todo remove center_x and center_y
            )
            flowchart.add_node(node)
        return flowcharts

    def get_flowchart_by_id(self, id):
        self.cursor.execute(
            "SELECT * FROM graph_view where id=%s", (id,)
        )  # todo select id,name from graph_view  for function get_graph_view
        # todo for function get_graph_view_to_flowchart_list select id,name from graph_view where id = input_id
        rows = self.cursor.fetchall()
        graph_nodes = row_results_to_class_list(GraphView, rows)

    def get_all_flowchart_ids_and_names(self):
        pass


if __name__ == "__main__":
    config = DatabaseConfig(
        host="172.18.0.3", database="postgres", user="postgres", password="postgres"
    )
    postgres_interface = PostgresInterface(config)
    graph_view = postgres_interface.get_graph_view()
    flowcharts = postgres_interface.graph_view_to_flowchart_list(graph_view)
    # print all nodes
    for flowchart in flowcharts:
        print(flowchart.nodes)
