from dataclasses import dataclass


@dataclass
class AssistantResponse:
    text: str
    image: bytes | None = None
