-- For Postgresql servers only
CREATE OR REPLACE FUNCTION get_graph_by_name(name TEXT) RETURNS graphs AS $$
    SELECT * FROM graphs WHERE name = $1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION serialize_graph_to_json(text name) returns JSON AS $$
    SELECT json_agg(row_to_json(t)) FROM (
        SELECT
            g.id,
            g.name,
            g.created,
            json_agg(row_to_json(n)) AS nodes
        FROM graphs g
        JOIN nodes n ON n.graph_id = g.id
        WHERE g.name = $1
        GROUP BY g.id
    ) t;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION serialize_graph_to_jsonb(text name) returns JSONB AS $$
    SELECT jsonb_agg(row_to_json(t)) FROM (
        SELECT
            g.id,
            g.name,
            g.created,
            jsonb_agg(row_to_json(n)) AS nodes
        FROM graphs g
        JOIN nodes n ON n.graph_id = g.id
        WHERE g.name = $1
        GROUP BY g.id
    ) t;
$$ LANGUAGE SQL;