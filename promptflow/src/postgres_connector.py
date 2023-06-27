from pydantic import BaseModel, ValidationError, validator
from datetime import datetime
from typing import Optional, List
import psycopg2


class GraphView(BaseModel):
    graph_id: int
    created: datetime
    graph_name: str
    node_label: str
    node_type_metadata: Optional[dict]
    node_type_name: str
    next_node: Optional[int]
    current_node: int
    conditional: Optional[str]
    has_conditional: bool


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


class PostgresConnector:
    def __init__(self, config: DatabaseConfig):
        self.conn = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password,
        )
        self.cursor = self.conn.cursor()

    def get_graph_view(self) -> List[GraphView]:
        self.cursor.execute("SELECT * FROM graph_view")
        rows = self.cursor.fetchall()

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
