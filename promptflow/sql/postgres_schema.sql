-- Node Types
CREATE TABLE IF NOT EXISTS node_types (
    id SERIAL PRIMARY KEY NOT NULL,
    name TEXT UNIQUE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_node_types_name ON node_types(name);

INSERT INTO node_types (name) VALUES 
  ('Start'),
  ('Input'),
  ('Print')
;

-- Graphs
CREATE TABLE IF NOT EXISTS graphs (
    id SERIAL PRIMARY KEY NOT NULL,
    name TEXT UNIQUE NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT current_timestamp
);

-- Nodes
CREATE TABLE IF NOT EXISTS nodes (
    id SERIAL PRIMARY KEY NOT NULL,
    node_type_id INTEGER REFERENCES node_types (id) ON UPDATE CASCADE ON DELETE CASCADE NOT NULL,
    graph_id INTEGER REFERENCES graphs (id) ON UPDATE CASCADE ON DELETE CASCADE NOT NULL,
    "label" TEXT NOT NULL,
    metadata JSONB NOT NULL
);

-- Branches
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY NOT NULL,
    conditional TEXT NOT NULL,
    label TEXT NOT NULL,
    node INTEGER REFERENCES nodes(id) ON UPDATE CASCADE ON DELETE CASCADE NOT NULL,
    next_node INTEGER REFERENCES nodes(id) ON UPDATE CASCADE ON DELETE CASCADE NOT NULL
);

-- Views
CREATE OR REPLACE VIEW graph_view AS
  SELECT
    g.id AS graph_id,
    g.created AS created,
    g."name" AS graph_name,
    n."label" AS node_label,
    n.metadata AS node_type_metadata,
    nt."name" AS node_type_name,
    b.next_node AS next_node,
    n.id AS current_node,
    b.conditional AS conditional,
    (SELECT COALESCE(b.conditional != '', FALSE)) AS has_conditional,
    b."label" AS branch_label,
    b.id AS branch_id
  FROM graphs g
  JOIN nodes n ON n.graph_id=g.id
  JOIN node_types nt ON nt.id=n.node_type_id
  LEFT OUTER JOIN branches b ON b.node=n.id;

-- Functions
CREATE OR REPLACE FUNCTION upsert_graph(p_input JSONB)
RETURNS TABLE (graph_id integer, graph_name TEXT)
LANGUAGE plpgsql
AS $$
DECLARE
  v_name text := p_input->>'name';
  nodes jsonb := p_input->'nodes';
  g_id integer;
BEGIN
    IF v_name IS NULL THEN RAISE EXCEPTION 'Name is required for upsert'; END IF;  
  
    SELECT g.id INTO g_id FROM graphs g WHERE g."name"=v_name;
    IF g_id IS NULL THEN 
      INSERT INTO graphs ("name") VALUES (v_name) RETURNING id INTO g_id;
    END IF;

    DELETE FROM nodes n WHERE n.graph_id=g_id;
  
    INSERT INTO nodes ("node_type_id", "graph_id", "label", "metadata") 
    SELECT  
      (j->>'node_type_id')::integer,
      g_id,
      j->>'name',
      j->'metadata'
    FROM 
      jsonb_array_elements(nodes) j;
  
    -- Return the ID of the new graph
    RETURN 
      query 
    SELECT 
      g_id,
      v_name;
END;
$$;

/*
DROP FUNCTION upsert_graph;
SELECT * FROM upsert_graph('{
  "name": "Frankie''s Graph",
  "nodes": [
    {
      "name": "Start",
      "node_type_id": 1,
      "metadata": {}
    },
    {
      "name": "Special Print",
      "node_type_id": 3,
      "metadata": {}
    }
  ]
}'::jsonb);
;

SELECT * FROM graphs g, nodes n WHERE n.graph_id=g.id;

-- BELOW HERE IS TESTING --
 

select * from node_types;
select * from graph_view;
 
// Upsert Graph Input 

{
  "name": "Frankie's Graph",
  "nodes": [
    {
      "name": "Start",
      "node_type_id": 2,
      "metadata": {
        "something": 123
      }
    }
  ]
}
 
 
 */

/*
INSERT INTO graphs ("name") VALUES ('Frankie''s Graph');
INSERT INTO node_types (metadata, name) VALUES ('{}'::jsonb, 'InputNode'), ('{}'::jsonb, 'LoggingNode');
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
