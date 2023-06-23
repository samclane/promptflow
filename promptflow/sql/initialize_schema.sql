BEGIN TRANSACTION;
PRAGMA foreign_keys = ON;

-- Graphs
CREATE TABLE IF NOT EXISTS graphs (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    created TIMESTAMP
);

-- Node Types
CREATE TABLE IF NOT EXISTS node_types (
    id SERIAL PRIMARY KEY,
    metadata JSON,
    name TEXT UNIQUE
);

-- Nodes
CREATE TABLE IF NOT EXISTS nodes (
    id SERIAL PRIMARY KEY,
    node_type_id INTEGER,
    graph_id INTEGER,
    label TEXT,
    FOREIGN KEY (node_type_id) REFERENCES node_types(id),
    FOREIGN KEY(graph_id) REFERENCES graphs(id)
);



-- Branches
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    conditional TEXT,
    label TEXT,
    node INTEGER,
    next_node INTEGER,
    FOREIGN KEY (node) REFERENCES nodes(id),
    FOREIGN KEY (next_node) REFERENCES nodes(id)
);

COMMIT;
