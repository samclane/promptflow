-- Graphs
CREATE TABLE IF NOT EXISTS graphs (
    id SERIAL PRIMARY KEY NOT NULL,
    name TEXT UNIQUE NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT current_timestamp
);

-- Node Types
CREATE TABLE IF NOT EXISTS node_types (
    id SERIAL PRIMARY KEY NOT NULL,
    metadata JSONB NOT NULL,
    name TEXT UNIQUE NOT NULL
);

-- Nodes
CREATE TABLE IF NOT EXISTS nodes (
    id SERIAL PRIMARY KEY NOT NULL,
    node_type_id INTEGER REFERENCES node_types (id) NOT NULL,
    graph_id INTEGER REFERENCES graphs (id) NOT NULL,
    "label" TEXT NOT NULL
);

-- Branches
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY NOT NULL,
    conditional TEXT NOT NULL,
    label TEXT NOT NULL,
    node INTEGER REFERENCES nodes(id) NOT NULL,
    next_node INTEGER REFERENCES nodes(id) NOT NULL
);

CREATE OR REPLACE VIEW graph_view AS
  SELECT
    g.id AS graph_id,
    g.created AS created,
    g."name" AS graph_name,
    n."label" AS node_label,
    nt.metadata AS node_type_metadata,
    nt."name" AS node_type_name,
    b.next_node AS next_node,
    n.id AS current_node,
    b.conditional AS conditional,
    (SELECT COALESCE(b.conditional != '', FALSE)) AS has_conditional
  FROM graphs g
  JOIN nodes n ON n.graph_id=g.id
  JOIN node_types nt ON nt.id=n.node_type_id
  LEFT OUTER JOIN branches b ON b.node=n.id;

-- BELOW HERE IS TESTING --

/*
INSERT INTO graphs ("name") VALUES ('Frankie''s Graph');
INSERT INTO node_types (metadata, name) VALUES ('{}'::jsonb, 'Input Node'), ('{}'::jsonb, 'Print Node');
INSERT INTO nodes (node_type_id, graph_id, "label") VALUES (1, 1, 'Input'), (2, 1, 'Output');
INSERT INTO branches (conditional, "label", node, next_node) VALUES ('', 'Print It', 1, 2);

INSERT INTO graphs ("name") VALUES ('Sawyer''s Graph');
INSERT INTO nodes (node_type_id, graph_id, "label") VALUES (1, 2, 'Input'), (2, 2, 'Output');
INSERT INTO branches (conditional, "label", node, next_node) VALUES ('', 'Sawyer''s Print It', 3, 4);

SELECT * FROM graph_view WHERE graph_id=2;
*/

/*
DROP TABLE graphs CASCADE;
DROP TABLE node_types CASCADE;
DROP TABLE nodes CASCADE;
DROP TABLE branches CASCADE;
*/
