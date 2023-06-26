BEGIN TRANSACTION;
PRAGMA foreign_keys = ON;

-- Graphs
CREATE TABLE IF NOT EXISTS graphs (
    id SERIAL PRIMARY KEY UNIQUE NOT NULL,
    name TEXT UNIQUE NOT NULL,
    created TIMESTAMP NOT NULL
);

-- Node Types
CREATE TABLE IF NOT EXISTS node_types (
    id SERIAL PRIMARY KEY UNIQUE NOT NULL,
    metadata JSON NOT NULL,
    name TEXT UNIQUE NOT NULL
);

-- Nodes
CREATE TABLE IF NOT EXISTS nodes (
    id SERIAL PRIMARY KEY UNIQUE NOT NULL,
    node_type_id INTEGER NOT NULL,
    graph_id INTEGER NOT NULL,
    label TEXT NOT NULL,
    FOREIGN KEY (node_type_id) REFERENCES node_types(id),
    FOREIGN KEY(graph_id) REFERENCES graphs(id)
);

-- Branches
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY UNIQUE NOT NULL,
    conditional TEXT NOT NULL,
    label TEXT NOT NULL,
    node INTEGER NOT NULL,
    next_node INTEGER NOT NULL,
    FOREIGN KEY (node) REFERENCES nodes(id),
    FOREIGN KEY (next_node) REFERENCES nodes(id)
);

COMMIT;
