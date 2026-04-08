"""
Production Agent Core 	60%+ Reliability Engine
No fluff. Pure execution.
"""

import json
import time
import traceback
import logging
from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AgentCore")


class TaskStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    RETRYING = "retrying"
    BLOCKED = "blocked"


@dataclass
class TaskResult:
    status: TaskStatus
    output: Any = None
    error: str = ""
    attempts: int = 0
    confidence: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class Tool:
    name: str
    description: str
    function: Callable
    required_params: list
    optional_params: list = field(default_factory=list)


class AgentCore:
    """
    The actual agent. No motivational speeches.
    Executes tasks, retries on failure, logs everything, learns from mistakes.
    """

    def __init__(
        self,
        llm_call: Callable,          # Your LLM API function
        max_retries: int = 3,
        confidence_threshold: float = 0.7,
        timeout: int = 120,
    ):
        self.llm_call = llm_call
        self.max_retries = max_retries
        self.confidence_threshold = confidence_threshold
        self.timeout = timeout
        self.tools: dict[str, Tool] = {}
        self.history: list[dict] = []
        self.system_prompt = self._build_system_prompt()
        self.success_count = 0
        self.total_count = 0

    def _build_system_prompt(self) -> str:
        return """You are an execution agent. You do not explain what you could do. You DO it.

RULES 	6 NEVER BREAK THESE:
1. EXECUTE first. Explain only if asked.
2. If a task needs a tool, call the tool. Do not describe calling it.
3. If you cannot do something, say exactly: \"BLOCKED: [reason]\"
4. If you are unsure, say: \"CLARIFY: [specific question]\"
5. Never give meta-advice about how to build agents.
6. Never output checklists about productivity.
7. Your output is the RESULT of the task, not a plan to do the task.

OUTPUT FORMAT (strict JSON):
{
    "action": "execute|clarify|blocked",
    "tool": "tool_name or null",
    "tool_params": {},
    "result": "the actual output/answer",
    "confidence": 0.0-1.0,
    "reasoning": "1-2 sentences max, only if complex"
}

If the user says "write code", you write the code.
If the user says "fix this", you fix it and return the fixed version.
If the user says "analyze", you analyze and return findings.
You are not a coach. You are a machine that executes."""

    def register_tool(self, tool: Tool):
        """Register a callable tool the agent can use."""
        self.tools[tool.name] = tool
        # Rebuild system prompt with tool awareness
        self.system_prompt = self._build_system_prompt() + self._tool_prompt()
        logger.info(f"Tool registered: {tool.name}")

    def _tool_prompt(self) -> str:
        if not self.tools:
            return ""
        lines = ["\n\nAVAILABLE TOOLS:"]
        for name, tool in self.tools.items():
            lines.append(
                f"- {name}: {tool.description} | params: {tool.required_params} | optional: {tool.optional_params}"
            )
        lines.append("\nTo use a tool, set 'tool' and 'tool_params' in your JSON output.")
        return "\n".join(lines)

    def execute(self, user_task: str, context: dict = None) -> TaskResult:
        """
        Main entry. Give it a task, get a result.
        Retries automatically. Logs everything.
        """
        self.total_count += 1
        context = context or {}

        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        # Inject recent history for continuity (last 5 turns)
        for h in self.history[-5:]:
            messages.append({"role": "user", "content": h.get("task", "")})
            messages.append({"role": "assistant", "content": h.get("response", "")})

        # Add context if provided
        if context:
            ctx_str = f"\n\nCONTEXT:\n{json.dumps(context, indent=2, default=str)}"
            user_task += ctx_str

        messages.append({"role": "user", "content": user_task})

        # --- Retry Loop ---
        last_error = ""
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Attempt {attempt}/{self.max_retries} for task: {user_task[:80]}...")

                raw_response = self._call_llm_with_timeout(messages)
                parsed = self._parse_response(raw_response)

                # --- Tool Execution ---
                if parsed.get("tool") and parsed["tool"] in self.tools:
                    tool_result = self._execute_tool(
                        parsed["tool"], parsed.get("tool_params", {})
                    )
                    parsed["result"] = tool_result
                    parsed["confidence"] = max(parsed.get("confidence", 0.8), 0.8)

                # --- Confidence Check ---
                confidence = parsed.get("confidence", 0.5)

                if parsed.get("action") == "blocked":
                    result = TaskResult(
                        status=TaskStatus.BLOCKED,
                        output=parsed.get("result"),
                        error=parsed.get("reasoning", ""),
                        attempts=attempt,
                        confidence=confidence,
                    )
                    self._log(user_task, raw_response, result)
                    return result

                if parsed.get("action") == "clarify":
                    result = TaskResult(
                        status=TaskStatus.PARTIAL,
                        output=parsed.get("result"),
                        attempts=attempt,
                        confidence=confidence,
                        metadata={"needs_clarification": True},
                    )
                    self._log(user_task, raw_response, result)
                    return result

                if confidence >= self.confidence_threshold:
                    self.success_count += 1
                    result = TaskResult(
                        status=TaskStatus.SUCCESS,
                        output=parsed.get("result"),
                        attempts=attempt,
                        confidence=confidence,
                    )
                    self._log(user_task, raw_response, result)
                    return result
                else:
                    # Low confidence  retry with a nudge
                    messages.append({"role": "assistant", "content": raw_response})
                    messages.append({
                        "role": "user",
                        "content": (
                            f"Your confidence was {confidence}. "
                            "That's too low. Try again with a better approach. "
                            "If you need a tool, use one. If you need to break the problem down, do it."
                        ),
                    })
                    last_error = f"Low confidence: {confidence}"

            except TimeoutError:
                last_error = f"Timeout on attempt {attempt}"
                logger.warning(last_error)
            except Exception as e:
                last_error = f"Error on attempt {attempt}: {str(e)}"
                logger.error(f"{last_error}\n{traceback.format_exc()}")
                # Feed error back for self-correction
                messages.append({
                    "role": "user",
                    "content": f"Previous attempt failed with error: {str(e)}. Fix and retry.",
                })

        # All retries exhausted
        result = TaskResult(
            status=TaskStatus.FAILED,
            error=last_error,
            attempts=self.max_retries,
        )
        self._log(user_task, "", result)
        return result

    def _call_llm_with_timeout(self, messages: list) -> str:
        """Call LLM with timeout protection."""
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.llm_call, messages)
            try:
                return future.result(timeout=self.timeout)
            except concurrent.futures.TimeoutError:
                raise TimeoutError(f"LLM call exceeded {self.timeout}s timeout")

    def _parse_response(self, raw: str) -> dict:
        """Extract structured JSON from LLM response. Handles messy outputs."""
        # Try direct JSON parse
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Try to find JSON block in response
        import re
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Fallback: treat entire response as result
        return {
            "action": "execute",
            "tool": None,
            "tool_params": {},
            "result": raw,
            "confidence": 0.6,
            "reasoning": "Raw response (no JSON structure detected)",
        }

    def _execute_tool(self, tool_name: str, params: dict) -> Any:
        """Actually run a tool. No pretending."""
        tool = self.tools[tool_name]

        # Validate required params
        missing = [p for p in tool.required_params if p not in params]
        if missing:
            raise ValueError(f"Tool '{tool_name}' missing required params: {missing}")

        logger.info(f"Executing tool: {tool_name} with params: {list(params.keys())}")
        result = tool.function(**params)
        logger.info(f"Tool '{tool_name}' completed successfully")
        return result

    def _log(self, task: str, response: str, result: TaskResult):
        """Log everything for debugging and improvement."""
        entry = {
            "timestamp": time.time(),
            "task": task[:200],
            "response": response[:500],
            "status": result.status.value,
            "confidence": result.confidence,
            "attempts": result.attempts,
            "error": result.error,
        }
        self.history.append(entry)
        logger.info(
            f"Task {'✅' if result.status == TaskStatus.SUCCESS else '❌'} "
            f"[{result.status.value}] confidence={result.confidence:.2f} attempts={result.attempts}"
        )

    @property
    def success_rate(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count

    def stats(self) -> dict:
        return {
            "total_tasks": self.total_count,
            "successes": self.success_count,
            "success_rate": f"{self.success_rate * 100:.1f}%",
            "history_length": len(self.history),
        }
