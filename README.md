---
title: AI Safety Review Environment
emoji: 🛡️
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
---

# AI Safety Review Environment

OpenEnv Hackathon environment for training agents to detect unsafe AI model outputs, bias, and jailbreak attempts.

## Tasks
The environment includes three safety review tasks:
- `easy`: Explicit content detection - flag harmful, violent, or explicit outputs
- `medium`: Bias detection - identify discriminatory or biased content
- `hard`: Jailbreak detection - detect attempts to bypass AI safety measures

## Entry points
- `inference.py`: Baseline inference script using OpenAI API for safety review.
- `server/app.py`: FastAPI server for OpenEnv compatibility.

## Configuration
Requires `openenv.yaml` to specify environment setup.
