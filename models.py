"""
AI Safety Review Environment – Pydantic Models
================================================
Defines observation, action, and reward structures for the safety review tasks.
Uses OpenEnv's Observation/Action base classes for full SDK compatibility.
"""

from typing import List, Dict, Literal, Optional, Any
from pydantic import BaseModel, Field
from openenv.core.env_server.types import Action, Observation, State


# ── Observation ──────────────────────────────────────────────────────────────

class SafetyObservation(Observation):
    """What the agent sees each step."""

    # The content being reviewed
    model_output: str = Field(
        ...,
        description="The AI model's output that needs safety review",
    )

    # Conversation context (critical for jailbreak detection)
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Previous messages in the conversation",
    )

    # Guidelines the agent should follow
    policy_guidelines: str = Field(
        ...,
        description="Relevant safety and content policies",
    )

    # Task metadata
    task_type: Literal[
        "explicit_content", "bias_detection", "jailbreak_detection"
    ] = Field(..., description="Type of safety review task")

    case_id: str = Field(..., description="Unique identifier for this test case")
    step_number: int = Field(..., ge=1, description="Current step in episode")
    max_steps: int = Field(..., ge=1, description="Maximum steps allowed")

    # Additional context for harder tasks
    user_profile: Optional[Dict[str, str]] = Field(
        None,
        description="User history/behaviour patterns (jailbreak detection)",
    )


# ── Action ───────────────────────────────────────────────────────────────────

class SafetyAction(Action):
    """What the agent outputs each step."""

    decision: Literal["APPROVE", "FLAG", "ESCALATE"] = Field(
        ...,
        description="Primary safety decision",
    )

    violation_type: Optional[Literal[
        # Explicit-content violations
        "hate_speech",
        "violence",
        "sexual_content",
        "self_harm",
        "dangerous_instructions",
        # Bias violations
        "gender_bias",
        "racial_bias",
        "religious_bias",
        "age_bias",
        "disability_bias",
        # Manipulation
        "jailbreak_attempt",
        "manipulation",
        # Other
        "misinformation",
        "policy_violation",
        "none",
    ]] = Field(None, description="Specific type of violation detected (if any)")

    severity: Optional[Literal["low", "medium", "high", "critical"]] = Field(
        None,
        description="Severity level of the violation",
    )

    reasoning: str = Field(
        ...,
        min_length=1,
        description="Clear explanation of the decision",
    )

    suggested_action: Optional[str] = Field(
        None,
        description="Recommended next steps or remediation",
    )

    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence in this decision (0–1)",
    )


# ── State ────────────────────────────────────────────────────────────────────

class SafetyState(State):
    """Internal state of the safety review environment."""

    # Episode tracking
    current_step: int = Field(
        default=0,
        ge=0,
        description="Current step in the episode",
    )

    total_steps: int = Field(
        default=0,
        ge=0,
        description="Total steps completed in episode",
    )

    current_case_id: str = Field(
        default="",
        description="Currently active test case ID",
    )

    # Statistics
    decisions_made: int = Field(
        default=0,
        description="Number of decisions made so far",
    )

    correct_decisions: int = Field(
        default=0,
        description="Number of correct decisions",
    )

    current_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Current score for this episode",
    )

    # Task context
    task_difficulty: Literal["easy", "medium", "hard"] = Field(
        default="easy",
        description="Current task difficulty level",
    )

    is_episode_done: bool = Field(
        default=False,
        description="Whether episode has ended",
    )

    episode_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Final episode results (if done)",
    )
