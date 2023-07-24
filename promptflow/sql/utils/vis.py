import psycopg2
from graphviz import Graph

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="172.21.0.2", database="promptflow", user="postgres", password="postgres"
)
cursor = conn.cursor()

# Get the table names
cursor.execute(
    """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    """
)
tables = cursor.fetchall()

# Create a graph
graph = Graph(engine="neato", graph_attr={"overlap": "false", "splines": "true"})

# Define shapes and colors for classes and attributes
class_shape = "box"
class_color = "lightblue"
attribute_shape = "ellipse"
attribute_color = "lightgray"
primary_key_color = "yellow"

# Iterate over the tables and their columns
for table in tables:
    table_name = table[0]
    graph.node(table_name, shape=class_shape, style="filled", fillcolor=class_color)

    # Get the column names and types for the current table
    cursor.execute(
        f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        """
    )
    columns = cursor.fetchall()

    # Add columns as child nodes (attributes) to the table node
    for column in columns:
        column_name, column_type = column
        attribute_node_name = f"{table_name}.{column_name}"
        graph.node(
            attribute_node_name,
            label=f"{column_name}: {column_type}",
            shape=attribute_shape,
            style="filled",
            fillcolor=attribute_color,
        )
        graph.edge(table_name, attribute_node_name)

    # Get foreign key relationships for the current table
    cursor.execute(
        f"""
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
        WHERE
            constraint_type = 'FOREIGN KEY' AND tc.table_name='{table_name}';
        """
    )
    foreign_keys = cursor.fetchall()

    # Add foreign key relationships to the graph
    for foreign_key in foreign_keys:
        source_table = table_name
        source_column = foreign_key[0]
        target_table = foreign_key[1]
        target_column = foreign_key[2]
        graph.edge(
            f"{source_table}.{source_column}",
            f"{target_table}.{target_column}",
            constraint="false",
            dir="forward",
        )

# Save the graph as a PDF file
graph.render("database_schema", format="pdf")

# Close the database connection
conn.close()
