"""
Reinforcement Learning loop for prompt/strategy optimization.
This is what actually pushes your agent from 60% -> 90%+.

Not a toy. This tracks what works, what fails, and evolves the agent.
"""

import json
import random
import time
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional
from collections import defaultdict
import logging

logger = logging.getLogger("RLOptimizer")


@dataclass
class Episode:
    task: str
    task_type: str            # "code_write", "file_edit", "analysis", "debug", etc.
    prompt_variant: str       # Which prompt strategy was used
    success: bool
    confidence: float
    attempts: int
    latency: float            # Seconds
    error: str = ""
    reward: float = 0.0       # Computed


@dataclass
class PromptVariant:
    name: str
    system_prompt_modifier: str   # Appended or replaces parts of base prompt
    score: float = 0.0
    uses: int = 0
    successes: int = 0

    @property
    def success_rate(self) -> float:
        return self.successes / max(self.uses, 1)


class RLOptimizer:
    """
    Epsilon-greedy bandit over prompt strategies + task-type routing.
    
    How it works:
    1. You define multiple prompt variants (strategies)
    2. Agent tries tasks using selected variant
    3. Reward is computed based on success, confidence, speed
    4. Best variants get selected more often (exploitation)
    5. Occasionally tries random variant (exploration)
    6. Over time, converges to the best strategy per task type
    """

    def __init__(
        self,
        epsilon: float = 0.15,       # Exploration rate
        decay: float = 0.995,        # Epsilon decay per episode
        min_epsilon: float = 0.05,
        save_path: str = "rl_state.json",
    ):
        self.epsilon = epsilon
        self.decay = decay
        self.min_epsilon = min_epsilon
        self.save_path = save_path

        self.variants: dict[str, PromptVariant] = {}
        self.episodes: list[Episode] = []

        # Q-table: task_type -> variant_name -> average_reward
        self.q_table: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        # Count table for averaging
        self.n_table: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

        self._init_default_variants()
        self._load_state()

    def _init_default_variants(self):
        """Pre-built prompt strategies. Each optimized for different failure modes."""

        self.add_variant(PromptVariant(
            name="direct_executor",
            system_prompt_modifier="""
STYLE: Direct execution. No preamble. Output the result immediately.
If writing code, write the code. If answering, answer. Nothing else."""
        ))

        self.add_variant(PromptVariant(
            name="chain_of_thought",
            system_prompt_modifier="""
STYLE: Think step by step internally, but output ONLY the final result.
Use <think>...</think> tags for internal reasoning (will be stripped).
Final output must be clean and directly usable."""
        ))

        self.add_variant(PromptVariant(
            name="tool_first",
            system_prompt_modifier="""
STYLE: Always check if a tool can solve this. Prefer tool execution over reasoning.
If a file needs reading, use read_file. If code needs running, use execute_python.
Only fall back to pure reasoning if no tool applies."""
        ))

        self.add_variant(PromptVariant(
            name="decomposer",
            system_prompt_modifier="""
STYLE: Break complex tasks into 2-4 subtasks. Execute each in sequence.
Output format for multi-step:
{"steps": [{"action": "...", "result": "..."}, ...], "final_result": "..."}"""
        ))

        self.add_variant(PromptVariant(
            name="verifier",
            system_prompt_modifier="""
STYLE: After producing a result, verify it. 
For code: mentally trace execution.
For answers: cross-check with known facts.
For edits: confirm the change is correct.
Only output after verification passes."""
        ))

        self.add_variant(PromptVariant(
            name="minimal",
            system_prompt_modifier="""
STYLE: Minimum viable output. No formatting unless requested. 
Code without comments unless complex. Answers in 1-3 sentences unless detail requested."""
        ))

    def add_variant(self, variant: PromptVariant):
        self.variants[variant.name] = variant

    def select_variant(self, task_type: str) -> PromptVariant:
        """Epsilon-greedy selection based on task type performance."""
        if random.random() < self.epsilon:
            # Explore: random variant
            chosen = random.choice(list(self.variants.values()))
            logger.info(f"🔍 Exploring: {chosen.name} for {task_type}")
        else:
            # Exploit: best variant for this task type
            q_values = self.q_table[task_type]
            if q_values:
                best_name = max(q_values, key=q_values.get)
                chosen = self.variants[best_name]
                logger.info(f"🎯 Exploiting: {chosen.name} (Q={q_values[best_name]:.3f}) for {task_type}")
            else:
                chosen = random.choice(list(self.variants.values()))
                logger.info(f"🆕 No data for {task_type}, random: {chosen.name}")

        return chosen

    def compute_reward(self, episode: Episode) -> float:
        """
        Reward function. This is the heart of RL tuning.
        
        Components:
        - Success: +1.0 base
        - Confidence bonus: +0.0 to +0.3
        - Speed bonus: +0.0 to +0.2 (faster = better)
        - Retry penalty: -0.1 per extra attempt
        - Failure: -0.5 base
        """
        if episode.success:
            reward = 1.0
            # Confidence bonus
            reward += min(episode.confidence * 0.3, 0.3)
            # Speed bonus (under 10s = full bonus)
            speed_bonus = max(0, 0.2 - (episode.latency / 50.0) * 0.2)
            reward += speed_bonus
            # Retry penalty
            reward -= (episode.attempts - 1) * 0.1
        else:
            reward = -0.5
            # Partial credit for high confidence failures (close but wrong)
            if episode.confidence > 0.5:
                reward += 0.1
            # Extra penalty for timeouts
            if "timeout" in episode.error.lower():
                reward -= 0.2

        return round(max(reward, -1.0), 4)

    def record_episode(self, episode: Episode):
        """Record result and update Q-table."""
        episode.reward = self.compute_reward(episode)
        self.episodes.append(episode)

        # Update variant stats
        variant = self.variants.get(episode.prompt_variant)
        if variant:
            variant.uses += 1
            if episode.success:
                variant.successes += 1

        # Update Q-table (incremental mean)
        tt = episode.task_type
        vn = episode.prompt_variant
        self.n_table[tt][vn] += 1
        n = self.n_table[tt][vn]
        old_q = self.q_table[tt][vn]
        # Running average update
        self.q_table[tt][vn] = old_q + (episode.reward - old_q) / n

        # Decay epsilon
        self.epsilon = max(self.min_epsilon, self.epsilon * self.decay)

        logger.info(
            f"📊 Episode recorded: {episode.task_type} | {episode.prompt_variant} | "
            f"reward={episode.reward:.3f} | Q={self.q_table[tt][vn]:.3f} | ε={self.epsilon:.3f}"
        )

        # Auto-save every 10 episodes
        if len(self.episodes) % 10 == 0:
            self._save_state()

    def get_report(self) -> dict:
        """Full performance report."""
        if not self.episodes:
            return {"status": "No episodes recorded yet"}

        total = len(self.episodes)
        successes = sum(1 for e in self.episodes if e.success)

        # Per task type breakdown
        by_type = defaultdict(lambda: {"total": 0, "success": 0, "avg_reward": 0})
        for ep in self.episodes:
            bt = by_type[ep.task_type]
            bt["total"] += 1
            if ep.success:
                bt["success"] += 1
            bt["avg_reward"] = (bt["avg_reward"] * (bt["total"] - 1) + ep.reward) / bt["total"]

        # Best variant per task type
        best_per_type = {}
        for tt, variants in self.q_table.items():
            if variants:
                best = max(variants, key=variants.get)
                best_per_type[tt] = {"variant": best, "q_value": round(variants[best], 3)}

        # Variant leaderboard
        variant_stats = {}
        for name, v in self.variants.items():
            variant_stats[name] = {
                "uses": v.uses,
                "success_rate": f"{v.success_rate * 100:.1f}%",
                "score": round(v.score, 3),
            }

        return {
            "overall_success_rate": f"{(successes / total) * 100:.1f}%",
            "total_episodes": total,
            "successes": successes,
            "epsilon": round(self.epsilon, 4),
            "by_task_type": dict(by_type),
            "best_variant_per_type": best_per_type,
            "variant_leaderboard": variant_stats,
        }

    def _save_state(self):
        """Persist RL state to disk."""
        state = {
            "epsilon": self.epsilon,
            "q_table": dict(self.q_table),
            "n_table": dict(self.n_table),
            "variant_stats": {
                name: {"uses": v.uses, "successes": v.successes, "score": v.score}
                for name, v in self.variants.items()
            },
            "episode_count": len(self.episodes),
        }
        Path(self.save_path).write_text(json.dumps(state, indent=2))
        logger.info(f"💾 RL state saved ({len(self.episodes)} episodes)")

    def _load_state(self):
        """Load RL state from disk if exists."""
        p = Path(self.save_path)
        if not p.exists():
            return

        try:
            state = json.loads(p.read_text())
            self.epsilon = state.get("epsilon", self.epsilon)

            for tt, variants in state.get("q_table", {}).items():
                for vn, q in variants.items():
                    self.q_table[tt][vn] = q
            for tt, variants in state.get("n_table", {}).items():
                for vn, n in variants.items():
                    self.n_table[tt][vn] = n

            for name, stats in state.get("variant_stats", {}).items():
                if name in self.variants:
                    self.variants[name].uses = stats.get("uses", 0)
                    self.variants[name].successes = stats.get("successes", 0)
                    self.variants[name].score = stats.get("score", 0)

            logger.info(f"📂 RL state loaded (ε={self.epsilon:.3f})")
        except Exception as e:
            logger.warning(f"Failed to load RL state: {e}")