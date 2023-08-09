"""
Handles all audio-related nodes
"""
import os
import wave
from abc import ABC
from typing import Any, Optional

import elevenlabs
import numpy as np
import openai

from promptflow.src.nodes.node_base import NodeBase
from promptflow.src.state import State
from promptflow.src.text_data import TextData

key = os.getenv("ELEVENLABS_API_KEY")
if key:
    elevenlabs.set_api_key(key)


class AudioNode(NodeBase, ABC):
    """
    Base class for handling audio
    """


class AudioInputNode(AudioNode, ABC):
    """
    Node for recording audio
    """

    data: Optional[list[float]] = None

    def before(self, state: State) -> Any:
        """
        Todo: Tell gui to get voice data
        """

    def run_subclass(self, before_result: Any, state) -> str:
        return state.result


class AudioOutputNode(AudioNode, ABC):
    """
    Node that plays back audio in some way
    """


class WhispersNode(AudioInputNode):
    """
    Uses OpenAI's Whispers API to transcribe audio
    """

    prompt: TextData
    filename: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = kwargs.get(
            "prompt", TextData("Whisper Prompt", "", self.flowchart)
        )

    def run_subclass(self, before_result: Any, state) -> str:
        super().run_subclass(before_result, state)
        transcript = openai.Audio.translate("whisper-1", open(self.filename, "rb"))
        if isinstance(transcript, dict):
            return transcript["text"]
        raise ValueError("Whispers API returned unexpected response" + str(transcript))

    def cost(self, state):
        price_per_minute = 0.006
        # get length of file in minutes
        with wave.open(self.filename, "rb") as wav_file:
            sample_rate = wav_file.getframerate()
            audio_data = np.frombuffer(
                wav_file.readframes(wav_file.getnframes()), dtype="int32"
            )
            duration = len(audio_data) / sample_rate
            return duration / 60 * price_per_minute

    def serialize(self):
        return super().serialize() | {
            "prompt": self.prompt.serialize(),
        }

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["prompt"]


class ElevenLabsNode(AudioOutputNode):
    """
    Uses ElevenLabs API to generate realistic speech
    """

    voice: str = "Bella"
    model: str = "eleven_monolingual_v1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voice = kwargs.get("voice", self.voice)
        self.model = kwargs.get("model", self.model)

    def run_subclass(self, before_result: Any, state) -> str:
        audio = elevenlabs.generate(
            text=state.result, voice="Bella", model="eleven_monolingual_v1"
        )
        if isinstance(audio, bytes):
            elevenlabs.play(audio)
        else:
            self.logger.warning("ElevenLabs API returned unexpected response" + str(audio))
        return state.result

    def serialize(self):
        return super().serialize() | {
            "voice": self.voice,
            "model": self.model,
        }

    def cost(self, state):
        # overage is $0.30 per 1000 characters
        return 0.30 * len(state.result) / 1000

    @staticmethod
    def get_option_keys() -> list[str]:
        return NodeBase.get_option_keys() + ["voice", "model"]
