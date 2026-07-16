import importlib
import importlib.metadata as metadata
from dataclasses import dataclass
from typing import Any, Dict, Mapping

from .workflow_config import AgentSpec


class QwenPawRuntimeUnavailable(RuntimeError):
    """Raised when the official QwenPaw runtime cannot be loaded."""


@dataclass
class QwenPawRuntimeInfo:
    package: str
    version: str


class QwenPawRuntimeBridge:
    """Thin bridge that verifies the official QwenPaw runtime is available."""

    def __init__(self, info: QwenPawRuntimeInfo) -> None:
        self.info = info

    @classmethod
    def from_environment(cls) -> "QwenPawRuntimeBridge":
        try:
            version = metadata.version("qwenpaw")
        except metadata.PackageNotFoundError as exc:
            raise QwenPawRuntimeUnavailable(
                "QwenPaw runtime is not installed. Install it with "
                "`python -m pip install qwenpaw`, then rerun with `--adapter real`."
            ) from exc

        try:
            importlib.import_module("qwenpaw")
        except Exception as exc:
            raise QwenPawRuntimeUnavailable(
                f"QwenPaw runtime is installed but cannot be imported: {exc}"
            ) from exc

        return cls(QwenPawRuntimeInfo(package="qwenpaw", version=version))

    def build_step(self, spec: AgentSpec, output: Any, output_count: int) -> Dict[str, Any]:
        return {
            "agent": spec.name,
            "module": spec.module,
            "status": "completed",
            "output_key": spec.output_key,
            "output_count": output_count,
            "message": spec.description,
            "runtime": self.info.package,
            "runtime_version": self.info.version,
            "output_type": _output_type(output),
        }


def _output_type(output: Any) -> str:
    if isinstance(output, Mapping):
        return "mapping"
    if isinstance(output, list):
        return "list"
    return type(output).__name__
