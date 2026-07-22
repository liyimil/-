import asyncio
import contextlib
import importlib
import importlib.metadata as metadata
import json
import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping

from .workflow_config import AgentSpec


class QwenPawRuntimeUnavailable(RuntimeError):
    """Raised when the official QwenPaw runtime cannot be loaded."""


@dataclass
class QwenPawRuntimeInfo:
    package: str
    version: str


class QwenPawRuntimeBridge:
    """Bridge to the official QwenPaw Agent runtime."""

    def __init__(self, info: QwenPawRuntimeInfo, runner: Any | None = None) -> None:
        self.info = info
        self.runner = runner

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

        return cls(
            QwenPawRuntimeInfo(package="qwenpaw", version=version),
            runner=QwenPawAgentRunner(),
        )

    def run_agent_workflow(
        self,
        tool_functions: Mapping[str, Callable[[], Mapping[str, Any]]],
        payload_summary: Mapping[str, Any],
    ) -> Dict[str, Any]:
        if self.runner is None:
            raise QwenPawRuntimeUnavailable("QwenPaw agent runner is not configured.")
        return self.runner.run_workflow(tool_functions, payload_summary)

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


class QwenPawAgentRunner:
    """Run local workflow tools through QwenPawAgent's ReAct loop."""

    def __init__(self, agent_id: str = "default", timeout_seconds: int = 180) -> None:
        self.agent_id = agent_id
        self.timeout_seconds = timeout_seconds

    def run_workflow(
        self,
        tool_functions: Mapping[str, Callable[[], Mapping[str, Any]]],
        payload_summary: Mapping[str, Any],
    ) -> Dict[str, Any]:
        try:
            from agentscope.message import TextBlock
            from agentscope.message import Msg
            from agentscope.tool import ToolResponse
            from qwenpaw.agents.react_agent import QwenPawAgent
            from qwenpaw.config.config import load_agent_config
        except Exception as exc:
            raise QwenPawRuntimeUnavailable(
                f"QwenPaw Agent API cannot be imported: {exc}"
            ) from exc

        agent_config = load_agent_config(self.agent_id)
        if not self._has_model_config(agent_config):
            raise QwenPawRuntimeUnavailable(
                "QwenPaw Agent is installed, but no active model is configured. "
                "Configure a QwenPaw model first, or use `--adapter demo` for "
                "the local deterministic workflow."
            )

        agent = QwenPawAgent(
            agent_config=agent_config,
            request_context={
                "session_id": "power-grid-orchestration",
                "user_id": "local-dashboard",
                "channel": "console",
                "agent_id": self.agent_id,
            },
        )
        for name, tool in tool_functions.items():
            agent.toolkit.register_tool_function(
                _as_qwenpaw_tool(name, tool, ToolResponse, TextBlock),
                namesake_strategy="override",
            )

        instruction = _build_agent_instruction(payload_summary, tool_functions.keys())
        with contextlib.redirect_stdout(sys.stderr):
            response = asyncio.run(
                asyncio.wait_for(
                    agent.reply([Msg(name="user", role="user", content=instruction)]),
                    timeout=self.timeout_seconds,
                )
            )

        return {
            "status": "completed",
            "response": response.get_text_content() if response else "",
        }

    def _has_model_config(self, agent_config: Any) -> bool:
        model_slot = getattr(agent_config, "active_model", None)
        if model_slot and getattr(model_slot, "provider_id", ""):
            return True
        try:
            from qwenpaw.providers import ProviderManager

            active_model = ProviderManager.get_instance().get_active_model()
            return bool(active_model and getattr(active_model, "provider_id", ""))
        except Exception:
            return False


def _build_agent_instruction(
    payload_summary: Mapping[str, Any],
    tool_names: Any,
) -> str:
    tools = ", ".join(f"`{name}`" for name in tool_names)
    return (
        "你是电网告警事件分析系统的调度智能体。"
        "请根据当前输入状态，决定并调用必要工具完成 A/B/C 主流程。"
        "可用工具为："
        f"{tools}。"
        "通常顺序为：先结构化告警，再进行 SKILL 匹配，最后完成规则表达式求值。"
        "必须通过工具调用完成模块执行，不要只在文本中描述。"
        "全部工具调用完成后，用一句话总结处理结果。"
        f"\n当前输入摘要：{dict(payload_summary)}"
    )


def _as_qwenpaw_tool(
    name: str,
    tool: Callable[[], Mapping[str, Any]],
    tool_response_cls: Any,
    text_block_cls: Any,
) -> Callable[[], Any]:
    def wrapped_tool() -> Any:
        result = tool()
        text = json.dumps(result, ensure_ascii=False)
        return tool_response_cls(content=[text_block_cls(type="text", text=text)])

    wrapped_tool.__name__ = name
    wrapped_tool.__doc__ = tool.__doc__
    return wrapped_tool
