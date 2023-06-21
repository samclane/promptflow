BEGIN TRANSACTION;

-- Graphs
CREATE TABLE IF NOT EXISTS graphs (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    created TIMESTAMP
);

-- Nodes
CREATE TABLE IF NOT EXISTS nodes (
    id SERIAL PRIMARY KEY,
    node_type_id INTEGER REFERENCES node_types(id),
    graph_id INTEGER REFERENCES graphs(id),
    label TEXT
);

-- Node Types
CREATE TABLE IF NOT EXISTS node_types (
    id SERIAL PRIMARY KEY,
    metadata JSON,
    name TEXT UNIQUE
);

-- Branches
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    node INTEGER REFERENCES nodes(id),
    conditional TEXT,
    label TEXT,
    next_node INTEGER REFERENCES nodes(id)
);

COMMIT;
