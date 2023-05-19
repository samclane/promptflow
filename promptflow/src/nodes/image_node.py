"""
Handles image data
"""
from abc import ABC
import base64
from PIL import Image, ImageTk
import io
from typing import Any

import customtkinter
from promptflow.src.dialogues.image_inspector import ImageInspector
from promptflow.src.nodes.node_base import NodeBase

import openai


class ImageNode(NodeBase, ABC):
    """
    Base class for image nodes
    """

    pass


class DallENode(ImageNode):
    """
    Call OpenAI's Dall-E API
    """

    n = 1
    size = "256x256"
    image = None

    def run_subclass(
        self, before_result: Any, state, console: customtkinter.CTkTextbox
    ) -> str:
        response = openai.Image.create(
            prompt=state.result, n=self.n, size=self.size, response_format="b64_json"
        )
        # show the image
        imgdata = base64.b64decode(response["data"][0]["b64_json"])
        pil_image = Image.open(io.BytesIO(imgdata))
        self.image = ImageTk.PhotoImage(pil_image)
        self.image_inspector = ImageInspector(self.canvas, self.image)
        self.canvas.wait_window(self.image_inspector)
        state.data = response["data"]
        return state.result
    
    def serialize(self) -> dict[str, Any]:
        return super().serialize() | {
            "n": self.n,
            "size": self.size,
        }
