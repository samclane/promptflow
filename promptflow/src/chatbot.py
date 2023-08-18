import json
import os
from typing import List, Optional

import openai
import requests
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from promptflow.src.node_map import node_map

openai.api_key = os.getenv("OPENAI_API_KEY")


class ChatMessage(BaseModel):
    """
    Class representing a message in a chat with the AI
    """

    sender: str
    text: str
    timestamp: str

    def convert_to_openai(self):
        """Converts a Message to the format expected by OpenAI's API"""
        return {
            "role": {"user": "user", "ai": "assistant"}[self.sender.lower()],
            "content": self.text,
        }


class ChatResponse(BaseModel):
    """A response from the chatbot"""

    user_message: ChatMessage
    ai_message: ChatMessage


class ChatbotOptions(BaseModel):
    """
    Options for the chatbot
    """

    model: str = "gpt-4"
    temperature: float = 1
    top_p: float = 1
    n: int = 1
    max_tokens: Optional[int] = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0


class Chatbot:
    """
    Holds the state of the chatbot and handles interactions with the OpenAI API
    including function calls and message generation
    """

    def __init__(self) -> None:
        self.messages = [
            {
                "role": "system",
                "content": """You are an AI assistant for the PromptFlow LLM creation and management tool. PromptFlow allows users to create flowcharts that string together Python functions and LLM tools. These flowcharts can then be executed and monitored remotely from a web client, mobile client, etc.
        Your job is to interface with the PromptFlow API in order to fulfill the user's requests. He may want to update an existing flowchart, create a new one, view running jobs, etc. You are a serious no bullshit chatbot. Act like one.

        Try not to guess the user's intent if you can avoid it. If anything is unclear ask the user. Don't make up values.
        """,
            }
        ]

        self.functions = [
            {
                "name": "get_flowcharts",
                "description": "Lists all available flowcharts available to the user.",
                "parameters": {
                    "type": "object",
                    "properties": {"action": {"type": "string"}},
                },
            },
            {
                "name": "upsert_flow_chart_by_id",
                "description": "Updates or inserts a flowchart or any of its components, given a flowchart id. This endpoint is stateless. It should include all of the information to create the new version of the flowchart. If someone wants to add or update a node, you must also include all of the other nodes and branches in your request otherwise they will get removed unintentionally.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "This is the user generated displayable name for this flowchart. Does not have to be unique",
                        },
                        "uid": {
                            "type": "string",
                            "description": "The user generated unique identifier of the flowchart.",
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
                                        "enum": list(node_map.keys()),
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
                                    "conditional": {
                                        "type": "string",
                                        "description": "This is the condition that must be met in order for this branch to be taken. This is a python expression that will be evaluated in the context of the flowchart.",
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
                "description": "Get an individual flowchart by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "flowchart_id": {
                            "type": "string",
                            "description": "The flowchart id you'd like to lookup.",
                        }
                    },
                },
            },
            {
                "name": "get_list_of_node_types",
                "description": "Lists all of the node types available to the user",
                "parameters": {
                    "type": "object",
                    "properties": {"action": {"type": "string"}},
                },
            },
            {
                "name": "run_flow_chart_by_id",
                "description": "Runs a flowchart given a flowchart ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "flowchart_id": {
                            "type": "string",
                            "description": "The flowchart id you'd like to run.",
                        }
                    },
                },
            },
            {
                "name": "get_all_jobs",
                "description": "Gets list of all jobs",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "graph_uid": {"type": "string"},
                        "status": {"type": "string"},
                        "limit": {"type": "integer"},
                    },
                },
            },
            {
                "name": "get_job_by_id",
                "description": "Gets a job by the job ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                        }
                    },
                },
            },
            {
                "name": "get_job_logs_by_id",
                "description": "Gets the logs for a job given the job id",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                        }
                    },
                },
            },
            {
                "name": "get_job_output",
                "description": "Gets the output for a job given the job id",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                        }
                    },
                },
            },
        ]

    @staticmethod
    def get_flowcharts(base: str) -> dict:
        return requests.get(base + "/flowcharts").json()

    @staticmethod
    def get_flowchart_by_id(base: str, args: dict) -> dict:
        id = args.get("flowchart_id", "")
        if not id:
            raise ValueError("flowchart_id is required")
        return requests.get(base + "/flowcharts/" + id).json()

    @staticmethod
    def upsert_flow_chart_by_id(base: str, args: dict) -> dict:
        return requests.post(base + "/flowcharts/", json=args).json()

    @staticmethod
    def get_list_of_node_types(base: str) -> dict:
        return requests.get(base + "/nodes/types").json()

    @staticmethod
    def run_flow_chart_by_id(base: str, args: dict) -> dict:
        id = args.get("flowchart_id", "")
        if not id:
            raise ValueError("flowchart_id is required")
        return requests.get(base + "/flowcharts/" + id + "/run", json=args).json()

    @staticmethod
    def get_all_jobs(base: str, args: dict) -> dict:
        return requests.get(base + "/jobs", json=args).json()

    @staticmethod
    def get_job_by_id(base: str, args: dict) -> dict:
        id = args.get("job_id", "")
        if not id:
            raise ValueError("job_id is required")
        return requests.get(base + "/jobs/" + id, json=args).json()

    @staticmethod
    def get_job_logs_by_id(base: str, args: dict) -> dict:
        id = args.get("job_id", "")
        if not id:
            raise ValueError("job_id is required")
        return requests.get(base + "/jobs/" + id + "/logs", json=args).json()

    @staticmethod
    def get_job_output(base: str, args: dict) -> dict:
        id = args.get("job_id", "")
        if not id:
            raise ValueError("job_id is required")
        return requests.get(base + "/jobs/" + id + "/output", json=args).json()

    def run_function(self, func_call: dict) -> dict:
        try:
            name = func_call.get("name")
            args_json = func_call.get("arguments", "{}")
            args = json.loads(args_json)
            base = "http://localhost:8000"  # TODO: change this to the real base url

            if name == "get_flowcharts":
                return self.get_flowcharts(base)
            elif name == "get_flowchart_by_id":
                return self.get_flowchart_by_id(base, args)
            elif name == "upsert_flow_chart_by_id":
                return self.upsert_flow_chart_by_id(base, args)
            elif name == "get_list_of_node_types":
                return self.get_list_of_node_types(base)
            elif name == "run_flow_chart_by_id":
                return self.run_flow_chart_by_id(base, args)
            elif name == "get_all_jobs":
                return self.get_all_jobs(base, args)
            elif name == "get_job_by_id":
                return self.get_job_by_id(base, args)
            elif name == "get_job_logs_by_id":
                return self.get_job_logs_by_id(base, args)
            elif name == "get_job_output":
                return self.get_job_output(base, args)
            else:
                raise ValueError(f"Unknown function name: {name}")
        except Exception as exc:
            return {"error": str(exc)}

    def create_chat_completion(
        self, messages_to_send: list, options: Optional[ChatbotOptions]
    ) -> dict:
        return openai.ChatCompletion.create(
            messages=messages_to_send,
            functions=self.functions,
            **options.dict() if options else {},
        )

    def process_function_call(
        self, message: dict, options: Optional[ChatbotOptions]
    ) -> dict:
        resp = self.run_function(message["function_call"])
        self.messages.append(
            {
                "role": "function",
                "name": message["function_call"]["name"],
                "content": json.dumps(resp),
            }
        )
        return self.create_chat_completion(self.messages, options)

    def get_message_content(
        self, user_convo: List[ChatMessage], options: Optional[ChatbotOptions]
    ) -> str:
        payload = list(map(lambda x: x.convert_to_openai(), user_convo))
        messages_to_send = self.messages + payload
        r = self.create_chat_completion(messages_to_send, options)
        if "choices" not in r:
            raise ValueError(f"Unexpected response from OpenAI: {r}")
        message = r["choices"][0]["message"]
        while message.get("function_call"):
            r = self.process_function_call(message, options)
            message = r["choices"][0]["message"]
        return message["content"]

    def chat(
        self, user_convo: List[ChatMessage], options: Optional[ChatbotOptions]
    ) -> str:
        """
        This function takes in a list of messages and returns a response from the model.
        """
        try:
            return self.get_message_content(user_convo, options)
        except Exception as e:
            return str(e)
