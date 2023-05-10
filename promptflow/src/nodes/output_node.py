"""
Nodes that output data to the user, such as text or files
"""

import tkinter as tk
from typing import Any
from promptflow.src.dialogues.multi_file import MultiFileInput

from promptflow.src.nodes.node_base import NodeBase


class FileOutput(NodeBase):
    """
    Outputs data to a file
    """

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
    ):
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(state.result)
        return state.result
