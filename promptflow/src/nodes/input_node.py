"""
Nodes that get run time input from the user
"""
import tkinter.simpledialog

from promptflow.src.nodes.node_base import Node

class InputNode(Node):
    """
    Node that prompts the user for input
    """

    def run_subclass(self, state):
        return tkinter.simpledialog.askstring(
            self.label, "Enter a value for this input:"
        )