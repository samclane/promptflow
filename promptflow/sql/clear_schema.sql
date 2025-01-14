DROP VIEW IF EXISTS graph_view;
DROP FUNCTION IF EXISTS upsert_graph(JSONB);
DROP FUNCTION IF EXISTS create_job(JSONB);
DROP PROCEDURE IF EXISTS create_job_log(JSONB);
DROP FUNCTION IF EXISTS update_job_status(JSONB);
DROP VIEW IF EXISTS jobs_view;
DROP TABLE IF EXISTS job_logs;
DROP TABLE IF EXISTS job_status;
DROP TABLE IF EXISTS job_metadata;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS job_statuses;
DROP TABLE IF EXISTS branches;
DROP TABLE IF EXISTS nodes;
DROP TABLE IF EXISTS graphs;
DROP INDEX IF EXISTS idx_nodes_graph_id_and_uid;
DROP TABLE IF EXISTS node_types;
DROP INDEX IF EXISTS idx_node_types_name;
