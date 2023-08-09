"""
Handles image data
"""
import base64
import io
import json
from abc import ABC
from enum import Enum
from typing import Any, Optional

import openai
import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor

from promptflow.src.nodes.node_base import NodeBase


class ImageSize(Enum):
    """
    Image sizes
    """

    s256x256 = "256x256"
    s512x512 = "512x512"
    s1024x1024 = "1024x1024"


class ImageNode(NodeBase, ABC):
    """
    Base class for image nodes
    """

    pass


class OpenImageFile(ImageNode):
    """
    Specify a file to open
    """

    filename = ""

    def run_subclass(self, before_result: Any, state) -> str:
        pil_image = Image.open(self.filename)
        self.image = pil_image
        state.data = self.image
        return state.result

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["filename"]


class JSONImageFile(ImageNode):
    """
    Open a file specified by input JSON
    """

    filename_key: str = "filename"

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.filename_key = kwargs.get("filename_key", "")

    def run_subclass(self, before_result: Any, state) -> str:
        try:
            data = json.loads(state.result)
        except json.decoder.JSONDecodeError:
            return "Invalid JSON"
        pil_image = Image.open(data[self.filename_key])
        self.image = pil_image
        state.data = self.image
        return state.result

    def serialize(self) -> dict[str, Any]:
        return super().serialize() | {
            "filename_key": self.filename_key,
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["filename_key"]


class DallENode(ImageNode):
    """
    Call OpenAI's Dall-E API
    """

    n = 1
    size = ImageSize.s256x256.value
    image: Optional[Image.Image] = None

    def run_subclass(self, before_result: Any, state) -> str:
        response = openai.Image.create(
            prompt=state.result,
            n=int(self.n),
            size=self.size,
            response_format="b64_json",
        )
        if not isinstance(response, dict):
            return f"Invalid response: {response}"
        # show the image
        imgdata = base64.b64decode(response["data"][0]["b64_json"])
        pil_image = Image.open(io.BytesIO(imgdata))
        self.image = pil_image
        state.data = self.image
        return state.result

    def serialize(self) -> dict[str, Any]:
        return super().serialize() | {
            "n": self.n,
            "size": self.size,
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["n", "size"]


class CaptionNode(ImageNode):
    """
    Caption an image
    """

    max_length = 50

    def run_subclass(self, before_result: Any, state) -> str:
        checkpoint = "microsoft/git-base"
        processor = AutoProcessor.from_pretrained(checkpoint)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pil_image = state.data
        inputs = processor(images=pil_image, return_tensors="pt").to(device)
        pixel_values = inputs.pixel_values
        model = AutoModelForCausalLM.from_pretrained(checkpoint)
        generated_ids = model.generate(
            pixel_values=pixel_values, max_length=int(self.max_length)
        )
        generated_caption = processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]
        return generated_caption

    def serialize(self) -> dict[str, Any]:
        return super().serialize() | {
            "max_length": self.max_length,
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["max_length"]


class SaveImageNode(ImageNode):
    """
    Save image to filename
    """

    filename: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = kwargs.get("filename", "")

    def run_subclass(self, before_result: Any, state) -> str:
        pil_image = state.data
        pil_image.save(self.filename)
        return state.result

    def serialize(self) -> dict[str, Any]:
        return super().serialize() | {
            "filename": self.filename,
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["filename"]
