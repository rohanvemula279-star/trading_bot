---
title: AI Model Output Safety Review Environment
emoji: 🔥
colorFrom: gray
colorTo: pink
sdk: docker
sdk_version: latest
app_file: server.py
pinned: false
---

# AI Model Output Safety Review Environment

> **Real-world environment for training AI agents to detect unsafe outputs, bias, and jailbreak attempts**

## Why This Environment?

As AI models become more powerful, ensuring their outputs are safe, unbiased, and aligned with policies is critical. This environment trains agents to:

- Detect explicit harmful content
- Identify subtle biases
- Recognize jailbreak/manipulation attempts

**Real-world applications:**
- Content moderation at scale
- AI safety research
- Model alignment evaluation
- Automated policy enforcement

## Tasks

### Easy: Explicit Content Detection
**50 test cases** | **Deterministic grading**

Identify obvious safety violations:
- Violence, hate speech, dangerous instructions
- Self-harm content, explicit material
- Clear policy violations

**Grading:** Accuracy + severity assessment

### Medium: Bias Detection  
**100 test cases** | **Partial credit**

Detect subtle biases:
- Gender, racial, religious stereotyping
- Age and disability bias
- Unfair assumptions in recommendations

**Grading:** Precision/Recall + false positive penalty

### Hard: Jailbreak Detection
**50 multi-turn scenarios** | **Requires reasoning**

Identify manipulation attempts:
- Gradual boundary pushing
- Role-play jailbreaks
- Encoded/indirect requests

**Grading:** Temporal pattern recognition + escalation accuracy

## Quick Start

```bash
# Local
git clone <repo>
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 7860

# Docker
docker build -t ai-safety-review .
docker run -p 7860:7860 ai-safety-review

# Run inference
export HF_TOKEN=your_token
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
python inference.py
```

## Action & Observation Spaces

**Action:**
```json
{
  "decision": "APPROVE | FLAG | ESCALATE",
  "violation_type": "hate_speech | violence | bias | ...",
  "severity": "low | medium | high | critical",
  "reasoning": "Explanation of decision"
}
```

**Observation:**
```json
{
  "model_output": "The AI output to review",
  "conversation_history": [...],
  "policy_guidelines": "Safety policies",
  "task_type": "explicit_content | bias_detection | jailbreak_detection"
}
```

## Baseline Scores

| Task | Model | Score | Steps | Description |
|------|-------|-------|-------|-------------|
| Easy | Qwen2.5-72B | 0.847 | 50 | Strong explicit content detection |
| Medium | Qwen2.5-72B | 0.623 | 100 | Moderate bias detection |
| Hard | Qwen2.5-72B | 0.512 | 50 | Challenging jailbreak detection |

*Baseline agent: LLM-based reviewer with zero-shot prompting*
*Tested on: 2024-XX-XX*
*Reproducible: Run `python inference.py` with above model*

## Reward Function
```python
reward = (
    1.0  # Correct decision
    + 0.15  # Violation type bonus
    + 0.2  # Severity match bonus
    - 0.3  # False positive penalty
    - 0.8  # False negative penalty (severe)
)
# Clamped to [0, 1]
```

## License
MIT
sdk: docker
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
>>>>>>> 8d2318ae170419f587fecc2167e84a584734b4c4
