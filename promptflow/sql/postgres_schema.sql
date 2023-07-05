-- Node Types
create table if not exists node_types (
  id SERIAL primary key not null,
  name text unique not null
);

create index if not exists idx_node_types_name on
node_types(name);

insert
	into
	node_types (name)
values
  ('StartNode'),
  ('InputNode'),
  ('PrintNode') on
conflict (name) do
update
set
	name = EXCLUDED.name;
-- Graphs
create table if not exists graphs (
  id SERIAL primary key not null,
  name text unique not null,
  created TIMESTAMP not null default current_timestamp
);
-- Nodes
create table if not exists nodes (
  id SERIAL primary key not null,
  uid text not null,
  node_type_id INTEGER references node_types (id) on
update
	cascade on
	delete
		cascade not null,
		graph_id INTEGER references graphs (id) on
		update
			cascade on
			delete
				cascade not null,
				"label" text not null,
				metadata JSONB not null,
				unique (graph_id,
				uid)
);

create index if not exists idx_nodes_graph_id_and_uid on
nodes(graph_id,
uid);
-- Branches
create table if not exists branches (
  id SERIAL primary key not null,
  conditional text not null,
  "label" text not null,
  graph_id integer not null,
  node text not null,
  next_node text not null,
  foreign key (graph_id,
node) references nodes(graph_id,
uid) on
delete
	cascade on
	update
		cascade,
		foreign key (graph_id,
		next_node) references nodes(graph_id,
		uid) on
		delete
			cascade on
			update
				cascade
);
-- Views
create
or replace
view graph_view as
select
	g.id as graph_id,
	g.created as created,
	g."name" as graph_name,
	n."label" as node_label,
	n.metadata as node_type_metadata,
	nt."name" as node_type_name,
	b.next_node as next_node,
	n.uid as current_node,
	b.conditional as conditional,
	(
	select
		coalesce(b.conditional != '', false)
  ) as has_conditional,
	b."label" as branch_label,
	b.id as branch_id,
	n.node_type_id as node_type_id
from
	graphs g
left join nodes n on
	n.graph_id = g.id
left join node_types nt on
	nt.id = n.node_type_id
left outer join branches b on
	b.node = n.uid;
-- Functions
create
or replace
function upsert_graph(p_input JSONB) 
returns table (
  graph_id integer,
  created timestamp,
  graph_name text,
  node_label text,
  node_metadata jsonb,
  node_type_name text,
  next_node text,
  current_node text,
  conditional text,
  has_conditional boolean,
  branch_label text,
  branch_id integer,
  node_type_id integer
) 
language plpgsql 
as $$
declare
v_name text := p_input ->> 'name';

nodes jsonb := p_input -> 'nodes';

branches jsonb := p_input -> 'branches';

g_id integer;

begin if v_name is null then raise exception 'Name is required for upsert';
end if;

select
	g.id
into
	g_id
from
	graphs g
where
	g."name" = v_name;

if g_id is null then
insert
	into
	graphs ("name")
values
  (v_name) returning id
into
	g_id;
end if;

delete
from
	nodes n
where
	n.graph_id = g_id;

insert
	into
	nodes (
    "uid",
	"node_type_id",
	"graph_id",
	"label",
	"metadata"
  )
select
	(j ->> 'uid') :: text,
	(j ->> 'node_type_id') :: integer,
	g_id,
	j ->> 'label',
	j -> 'metadata'
from
	jsonb_array_elements(nodes) j;

insert
	into
	branches (
    "conditional",
	"label",
	"graph_id",
	"node",
	"next_node"
  )
select
	b ->> 'conditional',
	b ->> 'label',
	g_id,
	b ->> 'prev',
	b ->> 'next'
from
	jsonb_array_elements(branches) b;
-- Return the ID of the new graph
return query
select
	*
from
	graph_view gv
where
	gv.graph_id = g_id;
end;

$$;
