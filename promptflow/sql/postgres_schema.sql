-- Node Types
CREATE TABLE IF NOT EXISTS node_types (
  id SERIAL PRIMARY KEY NOT NULL,
  name TEXT UNIQUE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_node_types_name ON node_types(name);

-- Graphs
CREATE TABLE IF NOT EXISTS graphs (
  id SERIAL PRIMARY KEY NOT NULL,
  uid TEXT UNIQUE NOT NULL,
  "label" TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT current_timestamp,
  image bytea
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
  uid TEXT NOT NULL,
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
  ON UPDATE CASCADE,
  UNIQUE (graph_id, uid)
);

-- Jobs
CREATE TABLE IF NOT EXISTS job_statuses (
  id serial PRIMARY KEY NOT NULL,
  status TEXT UNIQUE NOT NULL
);

INSERT INTO job_statuses (status) VALUES ('PENDING'), ('RUNNING'), ('FAILED'), ('DONE'), ('INPUT_REQUIRED') ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS jobs (
  id serial PRIMARY KEY NOT NULL,
  created timestamp NOT NULL DEFAULT current_timestamp,
  graph_id integer REFERENCES graphs(id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
  graph_uid TEXT REFERENCES graphs(uid) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL
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

CREATE TABLE IF NOT EXISTS job_output_types (
   type TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS job_outputs (
   job_id bigint REFERENCES jobs(id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
   output_type TEXT REFERENCES job_output_types(type) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL, 
   output TEXT
);

INSERT INTO job_output_types (type) VALUES ('JSON'), ('TEXT'), ('URL') ON CONFLICT (type) DO UPDATE SET type = EXCLUDED.type;

CREATE OR REPLACE VIEW jobs_view AS
  SELECT 
    j.id,
    js.status,
    j.created,
    js.created updated,
    jm.metadata,
    j.graph_id,
    g.uid graph_uid
  FROM
    jobs j
  JOIN graphs g ON g.id = j.graph_id
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
    TRUE
LEFT JOIN job_metadata jm ON jm.job_id = j.id;



CREATE OR REPLACE FUNCTION update_job_status (inp jsonb) RETURNS TABLE (id integer, status TEXT, created timestamp, updated timestamp, metadata jsonb, graph_id integer, graph_uid TEXT)
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

  RETURN query SELECT jv.id, jv.status, jv.created, jv.updated, jv.metadata, jv.graph_id, jv.graph_uid FROM jobs_view jv WHERE jv.id=job_id;
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

CREATE OR REPLACE FUNCTION create_job(inp jsonb) RETURNS TABLE (id integer, status TEXT, created timestamp, updated timestamp, metadata jsonb, graph_id integer, graph_uid TEXT) LANGUAGE plpgsql
AS $$
DECLARE
  job_id integer;
  graph_id integer := inp->>'graphId';
  graph_uid TEXT;
BEGIN
  IF graph_id IS NULL THEN RAISE EXCEPTION 'Graph ID is required'; END IF;
  SELECT g.uid INTO graph_uid FROM graphs g WHERE g.id = graph_id;
  INSERT INTO jobs (graph_id, graph_uid) VALUES (graph_id, graph_uid) RETURNING jobs.id INTO job_id;
  INSERT INTO job_metadata (metadata, job_id) VALUES (inp, job_id);
  INSERT INTO job_status (status_id, job_id) SELECT s.id, job_id FROM job_statuses s WHERE s.status='PENDING';
  RETURN query SELECT jv.id, jv.status, jv.created, jv.updated, jv.metadata, jv.graph_id, jv.graph_uid FROM jobs_view jv WHERE jv.id=job_id;
END $$;

CREATE OR REPLACE VIEW graph_view AS
  SELECT 
    g.id AS graph_id,
    g.created AS created,
    g."label" AS graph_name,
    g."uid" AS graph_uid,
    n."label" AS node_label,
    n.metadata AS node_type_metadata,
    nt."name" AS node_type_name,
    b.next_node AS next_node,
    n.uid AS current_node,
    COALESCE(b.conditional, '') AS conditional,
    (
    SELECT
      COALESCE(b.conditional != '', FALSE)
    ) AS has_conditional,
    b."label" AS branch_label,
    b.id AS branch_id,
    n.node_type_id AS node_type_id
  FROM nodes n
  JOIN node_types nt ON nt.id=n.node_type_id 
  JOIN graphs g ON g.id=n.graph_id
  LEFT JOIN branches b ON b.graph_id=g.id AND b.node=n.uid;

-- Functions
CREATE OR REPLACE FUNCTION upsert_graph(p_input JSONB) 
RETURNS TABLE (
  graph_id integer,
  created timestamp,
  graph_name TEXT,
  graph_uid TEXT,
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
v_label TEXT := p_input ->> 'label';
v_uid TEXT := p_input ->> 'uid';

nodes jsonb := p_input -> 'nodes';

branches jsonb := p_input -> 'branches';

g_id integer;

BEGIN 

  IF v_uid IS NULL THEN RAISE EXCEPTION 'UID is required for upsert'; END IF;
  IF v_label IS NULL THEN RAISE EXCEPTION 'Label is required for upsert'; END IF;

  SELECT g.id INTO g_id FROM graphs g WHERE g."uid" = v_uid;

  IF g_id IS NULL THEN
    INSERT INTO graphs ("label", "uid") VALUES (v_label, v_uid) RETURNING id INTO g_id;
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
    COALESCE(j -> 'metadata', '{}'::jsonb)
  FROM
    jsonb_array_elements(nodes) j;

  INSERT INTO branches (
    "conditional",
    "label",
    "uid",
    "graph_id",
    "node",
    "next_node"
  )
  SELECT
    COALESCE(b ->> 'conditional', ''),
    b ->> 'label',
    b ->> 'uid',
    g_id,
    b ->> 'prev',
    b ->> 'next'
  FROM
    jsonb_array_elements(branches) b;
  -- Return the ID of the new graph

  RETURN query SELECT * FROM graph_view gv WHERE gv.graph_id = g_id;
END $$;

INSERT INTO node_types (name) VALUES
     ('InitNode'),
     ('FileInput'),
     ('JSONFileInput'),
     ('FuncNode'),
     ('OpenAINode'),
     ('ClaudeNode'),
     ('GoogleVertexNode'),
     ('DateNode'),
     ('RandomNode'),
     ('HistoryNode'),
     ('ManualHistoryNode'),
     ('HistoryWindow'),
     ('WindowedHistoryNode'),
     ('DynamicWindowedHistoryNode'),
     ('DummyNode'),
     ('PromptNode'),
     ('EmbeddingInNode'),
     ('EmbeddingQueryNode'),
     ('EmbeddingsIngestNode'),
     ('AssertNode'),
     ('LoggingNode'),
     ('InterpreterNode'),
     ('EnvNode'),
     ('ManualEnvNode'),
     ('WhispersNode'),
     ('ElevenLabsNode'),
     ('PGQueryNode'),
     ('SQLiteQueryNode'),
     ('PGGenerateNode'),
     ('JsonNode'),
     ('JsonerizerNode'),
     ('SerpApiNode'),
     ('GoogleSearchNode'),
     ('FileOutput'),
     ('JSONFileOutput'),
     ('HttpNode'),
     ('JSONRequestNode'),
     ('ScrapeNode'),
     ('ServerInputNode'),
     ('PineconeInsertNode'),
     ('PineconeQueryNode'),
     ('DallENode'),
     ('CaptionNode'),
     ('OpenImageFile'),
     ('JSONImageFile'),
     ('SaveImageNode'),
     ('StartNode'),
     ('InputNode')
ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name;