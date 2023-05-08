"""
Nodes that get run time input from the user
"""
import tkinter as tk
from typing import Any
import customtkinter
from promptflow.src.dialogues.multi_file import MultiFileInput

from promptflow.src.nodes.node_base import NodeBase


class InputNode(NodeBase):
    """
    Node that prompts the user for input
    """

    def before(self, state, console):
        dialog = customtkinter.CTkInputDialog(
            text="Enter a value for this input:", title=self.label
        )
        return {"input": dialog.get_input()}

    def run_subclass(self, before_result, state, console):
        return before_result["input"]


class FileInput(NodeBase):
    """
    Reads a file and returns its contents
    """

    options_popup: MultiFileInput = None
    filename: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = kwargs.get("filename", "")

    def edit_options(self, event):
        self.options_popup = MultiFileInput(
            self.canvas,
            {
                "filename": self.filename,
            },
        )
        self.canvas.wait_window(self.options_popup)
        if self.options_popup.cancelled:
            return
        self.filename = self.options_popup.result["filename"]

    def run_subclass(
        self, before_result: Any, state, console: tk.scrolledtext.ScrolledText
    ) -> str:
        with open(self.filename, "r", encoding="utf-8") as f:
            return f.read()
