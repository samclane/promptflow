"""
Handles image data
"""
from abc import ABC
import base64
from PIL import Image, ImageTk
import io
from typing import Any
import torch
from transformers import AutoProcessor, AutoModelForCausalLM


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
        state.data = self.image
        return state.result

    def serialize(self) -> dict[str, Any]:
        return super().serialize() | {
            "n": self.n,
            "size": self.size,
        }


class CaptionNode(ImageNode):
    """
    Caption an image
    """

    def run_subclass(
        self, before_result: Any, state, console: customtkinter.CTkTextbox
    ) -> str:
        checkpoint = "microsoft/git-base"
        processor = AutoProcessor.from_pretrained(checkpoint)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # convert tkphotoimage to PIL image
        pil_image = ImageTk.getimage(state.data)
        inputs = processor(images=pil_image, return_tensors="pt").to(device)
        pixel_values = inputs.pixel_values
        model = AutoModelForCausalLM.from_pretrained(checkpoint)
        generated_ids = model.generate(pixel_values=pixel_values, max_length=50)
        generated_caption = processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]
        return generated_caption
