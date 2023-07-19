import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
import psycopg2.extensions
from pydantic import BaseModel, conint, constr, validator

from promptflow.src.connectors.connector import Connector
from promptflow.src.flowchart import Flowchart
from promptflow.src.node_map import node_map
from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.text_data import TextData


class JobView(BaseModel):
    """
    Model representing a job in the database

    Attributes:
        job_id (int): The unique ID of the job.
        job_status (str): The status of the job (PENDING'), ('RUNNING'), ('FAILED)
        created (datetime): The date and time the job was created.
        updated (datetime): The date and time the job was updated.
        metadata (Optional[Dict[str, Any]]): The metadata for the job.
        graph_id (Optional[int]): The ID of the graph associated with the job.
    """

    job_id: conint(gt=0)
    job_status: constr(min_length=1)
    created: datetime
    updated: datetime
    metadata: Optional[Dict[str, Any]]
    graph_id: Optional[conint(gt=0)]

    @staticmethod
    def hydrate(row: Tuple[Any, ...]) -> "JobView":
        """
        Hydrates a JobView instance from a dictionary representing a database row.

        Args:
            row (Dict[str, Any]): Dictionary representing a database row.

        Returns:
            JobView: A JobView instance populated with the data from the row.
        """
        return JobView(
            job_id=row[0],
            job_status=row[1],
            created=row[2],
            updated=row[3],
            metadata=row[4],
            graph_id=row[5],
        )


class GraphView(BaseModel):
    """
    Model representing a view of a graph.

    Attributes:
        graph_id (int): The unique ID of the graph.
        created (datetime): The date and time the graph was created.
        graph_name (str): The name of the graph.
        node_label (str): The label of a node in the graph.
        node_type_metadata (Optional[Dict[str, Any]]): The metadata for the type of node.
        node_type_name (str): The name of the node type.
        next_node (Optional[int]): The ID of the next node in the graph.
        current_node (int): The ID of the current node in the graph.
        conditional (Optional[str]): A conditional statement for node execution.
        has_conditional (bool): Indicates whether the node has a conditional statement.
    """

    graph_id: conint(gt=0)
    created: datetime
    graph_name: constr(min_length=1)
    node_label: Optional[constr(min_length=1)]
    node_type_metadata: Optional[Dict[str, Any]]
    node_type_name: Optional[constr(min_length=1)]
    next_node: Optional[constr(min_length=1)]
    current_node: Optional[constr(min_length=1)]
    conditional: Optional[str]
    has_conditional: bool
    branch_label: Optional[str]
    branch_id: Optional[conint(gt=0)]
    node_type_id: Optional[conint(gt=0)]

    @staticmethod
    def hydrate(row: Tuple[Any, ...]) -> "GraphView":
        """
        Hydrates a GraphView instance from a dictionary representing a database row.

        Args:
            row (Dict[str, Any]): Dictionary representing a database row.

        Returns:
            GraphView: A GraphView instance populated with the data from the row.
        """
        return GraphView(
            graph_id=row[0],
            created=row[1],
            graph_name=row[2],
            node_label=row[3],
            node_type_metadata=row[4],
            node_type_name=row[5],
            next_node=row[6],
            current_node=row[7],
            conditional=row[8],
            has_conditional=row[9],
            branch_label=row[10],
            branch_id=row[11],
            node_type_id=row[12],
        )


class DatabaseConfig(BaseModel):
    """
    Model representing the configuration for connecting to a database.

    Attributes:
        host (str): The host address of the database.
        database (str): The name of the database.
        user (str): The username for the database.
        password (str): The password for the database.
    """

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
    """
    Model representing the names and IDs of graphs.

    Attributes:
        id (int): The unique ID of the graph.
        name (str): The name of the graph.
    """

    id: int
    name: str

    @staticmethod
    def hydrate(row: Tuple[Any, ...]):
        return GraphNamesAndIds(id=row[0], name=row[1])


def row_results_to_class_list(class_name, list_of_rows):
    """
    Convert a list of rows to a list of class instances.

    Args:
        class_name (BaseModel): The class to be instantiated.
        list_of_rows (List[Tuple]): A list of rows where each row is a tuple of values.

    Returns:
        List[BaseModel]: A list of class instances.
    """
    return [class_name.hydrate(row) for row in list_of_rows]


def row_results_to_class(class_name, list_of_rows):
    """
    Return the first element of a list of class instances.
    """
    return row_results_to_class_list(class_name, list_of_rows)[0]


class DBInterface(ABC):
    """
    Acts as an db agnostic interface for interacting with a database.
    """

    def __init__(self, config: DatabaseConfig):
        """
        Initialize the PostgresInterface with a given configuration.

        Args:
            config (DatabaseConfig): The configuration for the database connection.
        """
        self.config: DatabaseConfig = config

    @abstractmethod
    def init_schema(self):
        """
        Run the initialize_schema.sql script to create the tables and functions
        """

    @abstractmethod
    def build_flowcharts_from_graph_view(
        self, graph_view: List[GraphView]
    ) -> List[Flowchart]:
        """
        Builds flowcharts from the graph views.

        Args:
            graph_view (List[GraphView]): List of graph views.

        Returns:
            List[Flowchart]: List of constructed flowcharts.
        """

    @abstractmethod
    def new_flowchart(self) -> Flowchart:
        """
        Creates a new flowchart in the database.
        """

    @abstractmethod
    def get_node_type_id(self, node_type):
        """
        Returns the node type ID for the given node type.
        """

    @abstractmethod
    def get_or_create_flowchart(
        self, flowcharts: List[Flowchart], row: GraphView
    ) -> Flowchart:
        """
        Get the flowchart with the matching graph_id from the list or create a new one if it doesn't exist.

        Args:
            flowcharts (List[Flowchart]): List of flowcharts.
            row (GraphView): The graph view to process.

        Returns:
            Flowchart: The flowchart that corresponds to the graph_id.
        """

    @staticmethod
    @abstractmethod
    def add_node_to_flowchart(flowchart: Flowchart, row: GraphView) -> NodeBase:
        """
        Add a node to the flowchart.

        Args:
            flowchart (Flowchart): The flowchart to which the node will be added.
            row (GraphView): The graph view containing node information.
        """

    @abstractmethod
    def add_connector_to_flowchart(self, flowchart: Flowchart, row: GraphView):
        """
        Add a connection between two nodes to the flowchart.

        Args:
            flowchart (Flowchart): The flowchart to which the connection will be added.
            row (GraphView): The graph view containing connection information.
        """

    @abstractmethod
    def get_flowchart_by_id(self, id) -> Flowchart:
        """
        Gets the flowchart from the database with the given ID.

        Args:
            id (int): The ID of the flowchart to retrieve.

        Returns:
            Flowchart: The flowchart with the given ID.
        """

    @abstractmethod
    def get_all_flowchart_ids_and_names(self) -> List[GraphNamesAndIds]:
        """
        Returns a list of all flowchart IDs and names.

        Args:
            None

        Returns:
            List[GraphNamesAndIds]: A list of all flowchart IDs and names.
        """

    @abstractmethod
    def save_flowchart(self, flowchart: Flowchart):
        """
        Saves the flowchart to the database.

        Args:
            flowchart (Flowchart): The flowchart to save.
        """

    @abstractmethod
    def delete_flowchart(self, flowchart_id: int):
        """
        Deletes the flowchart from the database.

        Args:
            flowchart_id (int): The ID of the flowchart to delete.
        """

    @abstractmethod
    def create_job(self, job: dict, flowchart_id: str):
        """
        Creates a new job in the database from a celery job.

        Args:
            job (Job): The job to create.
            flowchart_id (str): The ID of the flowchart to run.
        """

    @abstractmethod
    def update_job_status(self, job_id: int, status: str):
        """
        Updates the status of a job in the database.

        Args:
            job_id (int): The ID of the job to update.
            status (str): The new status of the job.
        """

    @abstractmethod
    def create_job_log(self, job_id: int, data: dict):
        """
        Creates a new job log in the database.

        Args:
            job_id (int): The ID of the job to update.
            log (dict): The log to create.
        """

    @abstractmethod
    def get_job_view(self, job_id: int) -> JobView:
        """
        Gets a job view from the database.

        Args:
            job_id (int): The ID of the job to retrieve.

        Returns:
            JobView: The job view with the given ID.
        """

    @abstractmethod
    def get_job_logs(self, job_id: int) -> List[dict]:
        """
        Gets a job log from the database.

        Args:
            job_id (int): The ID of the job to retrieve.

        Returns:
            List[dict]: The job log with the given ID.
        """


class PostgresInterface(DBInterface):
    """
    Interface for interacting with a PostgreSQL database.

    Attributes:
        config (DatabaseConfig): The configuration for the database connection.
        conn: The connection to the PostgreSQL database.
        cursor: The cursor for executing SQL queries.
    """

    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self.conn = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password,
        )
        self.init_schema()

    def init_schema(self):
        try:
            with open("promptflow/sql/postgres_schema.sql", "r") as file:
                with self.conn.cursor() as cursor:
                    cursor.execute(file.read())
                    self.conn.commit()
        except Exception as e:
            print(f"Error initializing schema: {e}")

    def build_flowcharts_from_graph_view(
        self, graph_view: List[GraphView]
    ) -> List[Flowchart]:
        flowcharts: List[Flowchart] = []

        for row in graph_view:
            flowchart = self.get_or_create_flowchart(flowcharts, row)
            if row.current_node:
                self.add_node_to_flowchart(flowchart, row)
            flowcharts.append(flowchart)

        # Todo: Add connectors to flowchart in a single pass
        for row in graph_view:
            flowchart = list(filter(lambda x: x.id == row.graph_id, flowcharts))[0]
            if row.next_node:
                self.add_connector_to_flowchart(flowchart, row)

        return flowcharts

    def new_flowchart(self) -> Flowchart:
        with self.conn.cursor() as cursor:
            name = {
                "name": "New Flowchart" + str(datetime.now()),
                "nodes": [],
                "branches": [],
            }
            cursor.callproc(
                """
                upsert_graph
                """,
                [
                    json.dumps(name),
                ],
            )
            self.conn.commit()
            row = cursor.fetchone()
            if not row:
                raise ValueError("No flowchart data returned from the database")
            id = row[0]
            return Flowchart(
                interface=self, id=id, name=name["name"], created=datetime.now()
            )

    def get_node_type_id(self, node_type):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id FROM node_types WHERE name = %s
                """,
                [node_type],
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Node type {node_type} not found")
            return row[0]

    def get_or_create_flowchart(
        self, flowcharts: List[Flowchart], row: GraphView
    ) -> Flowchart:
        existing_ids = [x.id for x in flowcharts]

        if row.graph_id not in existing_ids:
            flowchart = Flowchart(self, row.graph_id, row.graph_name, row.created)
            flowcharts.append(flowchart)
        else:
            flowchart = next((x for x in flowcharts if x.id == row.graph_id), None)
            if flowchart is None:
                raise ValueError(f"Flowchart with graph_id {row.graph_id} not found")

        return flowchart

    @staticmethod
    def add_node_to_flowchart(flowchart: Flowchart, row: GraphView) -> NodeBase:
        if not row.node_type_name:
            raise ValueError("Node type name cannot be null")
        node_cls = node_map.get(row.node_type_name)
        if node_cls is None:
            raise ValueError(f"Node type {row.node_type_name} not found in node_map")

        node = node_cls.deserialize(
            flowchart,
            (row.node_type_metadata or {})
            | {
                "label": row.node_label,
                "center_x": 0,
                "center_y": 0,
                "id": row.current_node,
                "node_type_id": row.node_type_id,
            },
        )

        flowchart.add_node(node)

        return node

    def add_connector_to_flowchart(self, flowchart: Flowchart, row: GraphView):
        # check if the connector is already in the flowchart
        if not row.branch_id:
            return
        if row.branch_id in map(lambda x: x.id, flowchart.connectors):
            return
        if not row.current_node or not row.next_node:
            return
        if not row.branch_label:
            row.branch_label = "Untitled"
        src_node = flowchart.find_node(row.current_node)
        dst_node = flowchart.find_node(row.next_node)
        if src_node and dst_node:
            connector = Connector(
                src_node,
                dst_node,
                TextData(row.branch_label, row.conditional, flowchart)
                if row.conditional
                else None,
                row.branch_id,
            )
            flowchart.add_connector(connector)

    def get_flowchart_by_id(self, id) -> Flowchart:
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM graph_view where graph_id=%s", (id,)
            )  # todo select id,name from graph_view  for function get_graph_view
            # todo for function get_graph_view_to_flowchart_list select id,name from graph_view where id = input_id
            rows = cursor.fetchall()
            self.conn.commit()
            graph_nodes = row_results_to_class_list(GraphView, rows)
            return self.build_flowcharts_from_graph_view(graph_nodes)[0]

    def get_all_flowchart_ids_and_names(self) -> List[GraphNamesAndIds]:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT id, name FROM graphs")
            rows = cursor.fetchall()
            self.conn.commit()
            return row_results_to_class_list(GraphNamesAndIds, rows)

    def save_flowchart(self, flowchart: Flowchart):
        with self.conn.cursor() as cursor:
            cursor.callproc(
                """
                upsert_graph
                """,
                [
                    json.dumps(flowchart.serialize()),
                ],
            )
            self.conn.commit()

    def delete_flowchart(self, flowchart_id: int):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM graphs WHERE id = %s
                """,
                [flowchart_id],
            )
            self.conn.commit()

    def create_job(self, job: dict, flowchart_id: str) -> int:
        with self.conn.cursor() as cursor:
            cursor.callproc(
                "create_job",
                [
                    json.dumps(job | {"graphId": flowchart_id}),
                ],
            )
            job_data = cursor.fetchone()
            if job_data is None:
                raise ValueError("Job creation failed")
            job_id = job_data[0]
            self.conn.commit()
            return job_id

    def update_job_status(self, job_id: int, status: str):
        with self.conn.cursor() as cursor:
            cursor.callproc(
                "update_job_status",
                [
                    json.dumps(
                        {
                            "jobId": job_id,
                            "status": status,
                        }
                    )
                ],
            )
            self.conn.commit()

    def create_job_log(self, job_id: int, data: dict):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "CALL create_job_log(%s)",
                (json.dumps({"jobId": job_id, "data": data}),),
            )
            self.conn.commit()

    def get_all_jobs(
        self, graph_id: str = None, status: str = None, limit: int = None
    ) -> List[JobView]:
        with self.conn.cursor() as cursor:
            query = """SELECT * FROM jobs_view"""
            if graph_id or status:
                query += """ WHERE"""
                if graph_id:
                    query += """ graph_id=%s""" % graph_id
                if graph_id and status:
                    query += """ AND"""
                if status:
                    query += """ status=%s""" % status
            if limit:
                query += """ LIMIT %s""" % str(limit)
            cursor.execute(
                query,
            )
            rows = cursor.fetchall()
            self.conn.commit()
            return list(map(JobView.hydrate, rows))

    def get_job_view(self, job_id: int) -> JobView:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM jobs_view where id=%s
                """,
                [job_id],
            )
            row = cursor.fetchone()
            self.conn.commit()
            if not row:
                raise ValueError(f"Job with id {job_id} not found")
            return JobView.hydrate(row)

    def get_job_logs(self, job_id: int) -> List[dict]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM job_logs where job_id=%s
                """,
                [job_id],
            )
            rows = cursor.fetchall()
            self.conn.commit()
            return list(map(lambda x: x[0], rows))

    def listener(self, manager, loop: asyncio.AbstractEventLoop):
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        with self.conn.cursor() as cur:
            cur.execute("LISTEN job_log_created;")

            while True:
                self.conn.poll()
                while self.conn.notifies:
                    notify = self.conn.notifies.pop(0)
                    loop.run_in_executor(
                        None, asyncio.run, manager.send_message(notify.payload)
                    )
