from pydantic import BaseModel, Field
from typing import Optional


class NmapScanInput(BaseModel):
    target: str
    ports: str = "1-1000"
    flags: list[str] = Field(default_factory=lambda: ["-Pn", "-sV"])


class GobusterDirInput(BaseModel):
    target: str
    wordlist: str
    extensions: list[str] = Field(default_factory=list)


class ToolResult(BaseModel):
    raw_output: str
    exit_code: int
    error: Optional[str] = None
    duration_ms: float
    extra: dict = Field(default_factory=dict)
