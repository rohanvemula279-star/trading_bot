---
title: AI Safety Review Environment
emoji: 🛡️
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
---

# LLM Quant Trading Environment

OpenEnv Hackathon environment for quant trading with LLMs.

## Tasks
The environment includes three trading tasks:
- `easy`: Basic trading signals
- `medium`: Multi-asset portfolio management
- `hard`: Risk-adjusted trading strategies

## Entry points
- `inference.py`: Baseline inference script using OpenAI API.
- `server/app.py`: FastAPI server for OpenEnv compatibility.

## Configuration
Requires `openenv.yaml` to specify environment setup.
