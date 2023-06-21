"""Main entry point for the promptflow application."""
import os
from promptflow.src.app import PromptFlowApp
from promptflow.src.state import State
from promptflow.src.options import Options


def main(*args, **kwargs):
    app = PromptFlowApp()


if __name__ == "__main__":
    main()
