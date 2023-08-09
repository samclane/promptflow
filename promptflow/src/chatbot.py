from typing import List
import openai
from pydantic import BaseModel  # pylint: disable=no-name-in-module
import requests
import json
import os
from  promptflow.src.node_map import node_map


class Message(BaseModel):
    sender: str
    text: str
    timestamp: str

    def convert_to_openai(self):
        return {
            "role": {"user": "user", "ai": "assistant"}[self.sender.lower()],
            "content": self.text,
        }


class ChatResponse(BaseModel):
    user_message: Message
    ai_message: Message


openai.api_key = os.getenv("OPENAI_API_KEY")
model = "gpt-4"

messages = [
    {
        "role": "system",
        "content": """You are an AI assistant for the PromptFlow LLM creation and management tool. PromptFlow allows users to create flowcharts that string together Python functions and LLM tools. These flow charts can then be executed and monitored remotely from a web client, mobile client, etc.
Your job is to interface with the PromptFlow API in order to fulfill the user's requests. He may want to update an existing flow chart, create a new one, view running jobs, etc. You are a serious no bullshit chatbot. Act like one.

Try not to guess the user's intent if you can avoid it. If anything is unclear ask the user. Don't make up values.
""",
    }
]

functions = [
    {
        "name": "get_flowcharts",
        "description": "Lists all available flowcharts available to the user.",
        "parameters": {"type": "object", "properties": {"action": {"type": "string"}}},
    },
    {
        "name": "upsert_flow_chart_by_id",
        "description": "Updates or inserts a flowchart given a name. This endpoint is stateless. It should include all of the information to create the new version of the flowchart. If someone wants to add or update a node, you must also include all of the other nodes and branches in your request otherwise they will get removed unintentionally.",
        "parameters": {
            "type": "object",
            "properties": {
                "label": {
                    "type": "string",
                    "description": "This is the user generated displayable name for this flow chart. Does not have to be unique",
                },
                "uid": {
                    "type": "string",
                    "description": "The user generated unique identifier of the flow chart.",
                },
                "nodes": {
                    "type": "array",
                    "description": "This is a list of the nodes in this flowchart.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "uid": {
                                "type": "string",
                                "description": "The unique identifier for this node. This is used by the branches array to create the branching.",
                            },
                            "label": {
                                "type": "string",
                                "description": "The user generated identifier for this node.",
                            },
                            "node_type": {
                                "type": "string",
                                "enum": list(
                                    node_map.keys()
                                ),
                                "description": "This is the name of the node type as it appears in the database. This value can be acquired from the get_list_of_node_types function.",
                            },
                        },
                    },
                },
                "branches": {
                    "type": "array",
                    "description": "This is a list of the connections between nodes in this flowchart.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "uid": {
                                "type": "string",
                                "description": "This is the user generated unique identifier for this branch",
                            },
                            "label": {
                                "type": "string",
                                "description": "The user generated identifier for this branch.",
                            },
                            "prev": {
                                "type": "string",
                                "description": "This field should reference the 'uid' of the node in the nodes array from which the connection starts.",
                            },
                            "next": {
                                "type": "string",
                                "description": "This field should reference the 'uid' of the node in the nodes array to which the connector points.",
                            },
                        },
                    },
                },
            },
        },
        "required": ["uid", "nodes", "branches"],
    },
    {
        "name": "get_flowchart_by_id",
        "description": "Get an individual flow chart by ID",
        "parameters": {
            "type": "object",
            "properties": {
                "flowchart_id": {
                    "type": "string",
                    "description": "The flow chart id you'd like to lookup.",
                }
            },
        },
    },
    {
        "name": "get_list_of_node_types",
        "description": "Lists all of the node types available to the user",
        "parameters": {"type": "object", "properties": {"action": {"type": "string"}}},
    },
]
"""
    {
        "name": "run_flow_chart_by_id",
        "description": "Runs a flow chart given an ID"
    },
    {
        "name": "get_all_jobs",
        "description": "Gets list of all jobs"
    },
    {
        "name": "get_job_by_id",
        "description": "Gets a job by the job ID"
    },
    {
        "name": "get_job_logs_by_id",
        "description": "Gets the logs for a job given the job id"
    },
"""


def run_function(r):
    name = r["name"]
    args = json.loads(r["arguments"])

    base = "http://localhost:8000"  # TODO: change this to the real base url
    if name == "get_flowcharts":
        return requests.get(base + "/flowcharts").json()
    elif name == "get_flowchart_by_id":
        id = args.get("flowchart_id", "")
        return requests.get(base + "/flowcharts/" + id).json()
    elif name == "upsert_flow_chart_by_id":
        return requests.post(base + "/flowcharts/", json=args).json()
    elif name == "get_list_of_node_types":
        return requests.get(base + "/nodes/types").json()


def chat(user_convo: List[Message]) -> str:
    """
    This function takes in a list of messages and returns a response from the model.
    """
    payload = list(map(lambda x: x.convert_to_openai(), user_convo))
    # combine payload and `messages` into one list
    messages_to_send = messages + payload

    r = openai.ChatCompletion.create(
        model=model, messages=messages_to_send, functions=functions
    )
    message = r["choices"][0]["message"]
    while message.get("function_call"):
        resp = run_function(message["function_call"])
        messages.append(
            {
                "role": "function",
                "name": message["function_call"]["name"],
                "content": json.dumps(resp),
            }
        )
        r = openai.ChatCompletion.create(
            model=model, messages=messages, functions=functions
        )
        message = r["choices"][0]["message"]
    return message["content"]
