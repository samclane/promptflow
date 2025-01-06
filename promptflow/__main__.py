"""Main entry point for the promptflow application."""
from promptflow.src.app import PromptFlowApp


def main(*args, **kwargs):
    app = PromptFlowApp()


if __name__ == "__main__":
    main()
