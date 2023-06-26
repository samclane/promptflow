import sqlite3
from graphviz import Graph

# Connect to the SQLite database
conn = sqlite3.connect("flowcharts.db")
cursor = conn.cursor()

# Get the table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

# Create a graph
graph = Graph(engine="neato", graph_attr={"overlap": "false", "splines": "true"})

# Define shapes and colors for classes and attributes
class_shape = "box"
class_color = "lightblue"
attribute_shape = "ellipse"
attribute_color = "lightgray"

# Iterate over the tables and their columns
for table in tables:
    table_name = table[0]
    graph.node(
        table_name, shape=class_shape, style="filled", fillcolor=class_color
    )  # Add table node (class) to the graph

    # Get the column names and types for the current table
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    columns = cursor.fetchall()

    # Add columns as child nodes (attributes) to the table node
    for column in columns:
        column_name = column[1]
        column_type = column[2]
        attribute_node_name = f"{table_name}.{column_name}"
        graph.node(
            attribute_node_name,
            label=f"{column_name}: {column_type}",
            shape=attribute_shape,
            style="filled",
            fillcolor=attribute_color,
        )
        graph.edge(table_name, attribute_node_name)

    # Get foreign key constraints for the current table
    cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
    foreign_keys = cursor.fetchall()

    # Add foreign key relationships to the graph
    for foreign_key in foreign_keys:
        source_table = table_name
        source_column = foreign_key[3]
        target_table = foreign_key[2]
        target_column = foreign_key[4]
        graph.edge(
            f"{source_table}.{source_column}",
            f"{target_table}.{target_column}",
            constraint="false",
            dir="forward",
            arrowhead="vee",
        )

# Save the graph as a PDF file
graph.render("database_schema", format="pdf")

# Close the database connection
conn.close()
