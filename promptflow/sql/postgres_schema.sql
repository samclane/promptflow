-- Jobs
CREATE TABLE IF NOT EXISTS job_statuses (
  id serial PRIMARY KEY NOT NULL,
  status TEXT UNIQUE NOT NULL
);

INSERT INTO job_statuses (status) VALUES ('PENDING'), ('RUNNING'), ('FAILED'), ('DONE') ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS jobs (
  id serial PRIMARY KEY NOT NULL,
  created timestamp NOT NULL DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS job_metadata (
  id serial PRIMARY KEY NOT NULL,
  job_id bigint REFERENCES jobs(id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
  metadata jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS job_status (
  status_id bigint REFERENCES job_statuses(id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
  job_id bigint REFERENCES jobs(id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
  created timestamp NOT NULL DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS job_logs (
  "log" json,
  job_id bigint REFERENCES jobs(id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
  created timestamp NOT NULL DEFAULT current_timestamp
);

CREATE OR REPLACE VIEW jobs_view AS
  SELECT 
    j.id,
    js.status,
    j.created,
    js.created updated,
    jm.metadata
FROM
  jobs j
  LEFT JOIN job_metadata jm ON jm.job_id = j.id
  JOIN LATERAL (
    SELECT
      js.job_id,
      jss.status,
      js.created
    FROM
      job_status js
    JOIN job_statuses jss ON
      jss.id = js.status_id
    WHERE 
      j.id = js.job_id
    ORDER BY
      js.created DESC
    LIMIT 1
      ) AS js ON
    TRUE;


CREATE OR REPLACE FUNCTION update_job_status (inp jsonb) RETURNS TABLE (id integer, status TEXT, created timestamp, updated timestamp, metadata jsonb)
LANGUAGE plpgsql 
AS $$ 
DECLARE
  s TEXT := inp->>'status';
  s_id integer;
  job_id integer := inp->>'jobId';
BEGIN
  IF s IS NULL THEN RAISE EXCEPTION 'Status is required'; END IF;
  IF job_id IS NULL THEN RAISE EXCEPTION 'Job ID is required'; END IF;
  SELECT js.id INTO s_id FROM job_statuses js WHERE js.status=s;
  IF s_id IS NULL THEN RAISE EXCEPTION 'Invalid status'; END IF;

  INSERT INTO job_status (status_id, job_id) VALUES (s_id, job_id);

  RETURN query SELECT jv.id, jv.status, jv.created, jv.updated, jv.metadata FROM jobs_view jv WHERE jv.id=job_id;
END $$;

CREATE OR REPLACE PROCEDURE create_job_log(inp jsonb) LANGUAGE plpgsql AS $$ 
DECLARE 
  job_id integer := inp->>'jobId';
  "log" jsonb := inp->'data';
BEGIN
  IF job_id IS NULL THEN RAISE EXCEPTION 'Job ID is required'; END IF;
  IF "log" IS NULL THEN RAISE EXCEPTION 'Log data is required'; END IF;
  INSERT INTO job_logs (job_id, "log") VALUES (job_id, "log");
END $$;

CREATE OR REPLACE FUNCTION create_job(inp jsonb) RETURNS TABLE (id integer, status TEXT, created timestamp, updated timestamp, metadata jsonb) LANGUAGE plpgsql
AS $$
DECLARE
  job_id integer;
BEGIN
  INSERT INTO jobs DEFAULT VALUES RETURNING jobs.id INTO job_id;
  INSERT INTO job_metadata (metadata, job_id) VALUES (inp, job_id);
  INSERT INTO job_status (status_id, job_id) SELECT s.id, job_id FROM job_statuses s WHERE s.status='PENDING';
  RETURN query SELECT jv.id, jv.status, jv.created, jv.updated, jv.metadata FROM jobs_view jv WHERE jv.id=job_id;
END $$;

-- Node Types
CREATE TABLE IF NOT EXISTS node_types (
  id SERIAL PRIMARY KEY NOT NULL,
  name TEXT UNIQUE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_node_types_name ON node_types(name);

INSERT
  INTO
  node_types (name)
VALUES
  ('StartNode'),
  ('InputNode')
ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name;

-- Graphs
CREATE TABLE IF NOT EXISTS graphs (
  id SERIAL PRIMARY KEY NOT NULL,
  name TEXT UNIQUE NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT current_timestamp
);
-- Nodes
CREATE TABLE IF NOT EXISTS nodes (
  id SERIAL PRIMARY KEY NOT NULL,
  uid TEXT NOT NULL,
  node_type_id INTEGER REFERENCES node_types (id) ON UPDATE CASCADE ON DELETE CASCADE NOT NULL,
  graph_id INTEGER REFERENCES graphs (id) ON UPDATE CASCADE ON DELETE CASCADE NOT NULL,
  "label" TEXT NOT NULL,
  metadata JSONB NOT NULL,
  UNIQUE (graph_id, uid)
);

CREATE INDEX IF NOT EXISTS idx_nodes_graph_id_and_uid ON nodes(graph_id, uid);
-- Branches
CREATE TABLE IF NOT EXISTS branches (
  id SERIAL PRIMARY KEY NOT NULL,
  conditional TEXT NOT NULL,
  "label" TEXT NOT NULL,
  graph_id integer NOT NULL,
  node TEXT NOT NULL,
  next_node TEXT NOT NULL,
  FOREIGN KEY (graph_id, node) REFERENCES nodes(graph_id, uid) 
  ON DELETE CASCADE 
  ON UPDATE CASCADE,
  FOREIGN KEY (graph_id, next_node) REFERENCES nodes(graph_id, uid) 
  ON DELETE CASCADE 
  ON UPDATE CASCADE
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
    n.uid AS current_node,
    b.conditional AS conditional,
    (
    SELECT
      COALESCE(b.conditional != '', FALSE)
    ) AS has_conditional,
    b."label" AS branch_label,
    b.id AS branch_id,
    n.node_type_id AS node_type_id
  FROM
    graphs g
  LEFT JOIN nodes n ON
    n.graph_id = g.id
  LEFT JOIN node_types nt ON
    nt.id = n.node_type_id
  LEFT OUTER JOIN branches b ON
    b.node = n.uid;

-- Functions
CREATE OR REPLACE FUNCTION upsert_graph(p_input JSONB) 
RETURNS TABLE (
  graph_id integer,
  created timestamp,
  graph_name TEXT,
  node_label TEXT,
  node_metadata jsonb,
  node_type_name TEXT,
  next_node TEXT,
  current_node TEXT,
  conditional TEXT,
  has_conditional boolean,
  branch_label TEXT,
  branch_id integer,
  node_type_id integer
) 
LANGUAGE plpgsql 
AS $$
DECLARE
v_name TEXT := p_input ->> 'name';

nodes jsonb := p_input -> 'nodes';

branches jsonb := p_input -> 'branches';

g_id integer;

BEGIN 
  /*

{
    "name": "My Graph",
    "nodes": [
      {
        "uid": "1",
        "node_type": "InitNode",
        "label": "Initializer Node",
        "metadata": {
          "field1": "Okay"
        }
      }
    ],
    "branches": [
      {
        "conditional": "",
        "label": "Loop it",
        "prev": "1",
        "next": "1"
      }
    ]
}
  
   */
  
  IF v_name IS NULL THEN RAISE EXCEPTION 'Name is required for upsert'; END IF;

  SELECT g.id INTO g_id FROM graphs g WHERE g."name" = v_name;

  IF g_id IS NULL THEN
    INSERT INTO graphs ("name") VALUES (v_name) RETURNING id INTO g_id;
  END IF;

  DELETE FROM nodes n WHERE n.graph_id = g_id;

  INSERT INTO nodes (
    "uid",
    "node_type_id",
    "graph_id",
    "label",
    "metadata"
  )
  SELECT
    (j ->> 'uid') :: TEXT,
    (SELECT id FROM node_types  WHERE "name"=(j ->> 'node_type')) AS node_type_id,
    g_id,
    j ->> 'label',
    j -> 'metadata'
  FROM
    jsonb_array_elements(nodes) j;

  INSERT INTO branches (
    "conditional",
    "label",
    "graph_id",
    "node",
    "next_node"
  )
  SELECT
    b ->> 'conditional',
    b ->> 'label',
    g_id,
    b ->> 'prev',
    b ->> 'next'
  FROM
    jsonb_array_elements(branches) b;
  -- Return the ID of the new graph

  RETURN query SELECT * FROM graph_view gv WHERE gv.graph_id = g_id;
END $$;

