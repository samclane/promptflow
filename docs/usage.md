(Usage)=
# PromptFlow

PromptFlow is a Python application for creating and running conversational AI pipelines. It provides a drag and drop interface for building pipelines and leverages FastAPI for the backend API.

## API Reference

### Flowcharts

- `GET /flowcharts` - Get all flowcharts

- `POST /flowcharts` - Upsert a flowchart from JSON

- `GET /flowcharts/(str:flowchart_id)` - Get a flowchart by ID

- `GET /flowcharts/(str:flowchart_id)/run` - Run a flowchart execution as a background task 

- `GET /flowcharts/(str:flowchart_id)/stop` - Stop a running flowchart

- `GET /flowcharts/(str:flowchart_id)/clear` - Clear a flowchart's state

- `GET /flowcharts/(str:flowchart_id)/cost` - Get estimated cost to run flowchart

- `POST /flowcharts/(str:flowchart_id)/save_as` - Serialize flowchart and save to a ZIP file

- `POST /flowcharts/load_from` - Load flowchart from a ZIP file

### Jobs

- `GET /jobs` - Get all jobs

- `GET /jobs/(int:job_id)` - Get a job by ID

- `GET /jobs/(int:job_id)/logs` - Get logs for a job  

- `WEBSOCKET /jobs/(int:job_id)/ws` - Websocket for streaming job logs

### Nodes

- `GET /nodes/types` - Get all node types

- `POST /flowcharts/(str:flowchart_id)/nodes` - Add a node to a flowchart

- `DELETE /flowcharts/(str:flowchart_id)/nodes/(str:node_id)` - Remove a node from a flowchart

- `POST /flowcharts/(str:flowchart_id)/nodes/(str:node_id)/connect` - Connect two nodes

- `GET /flowcharts/(str:flowchart_id)/nodes/(str:node_id)/options` - Get a node's options

- `POST /flowcharts/(str:flowchart_id)/nodes/(str:node_id)/options` - Update a node's options

## Websocket

The `/jobs/(int:job_id)/ws` websocket endpoint streams job logs in real-time as JSON.
