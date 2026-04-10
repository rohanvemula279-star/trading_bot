# AI Safety Review Environment

OpenEnv Hackathon environment for safety review.

## Tasks
The environment includes three safety review tasks:
- `easy`: Explicit content detection
- `medium`: Bias detection
- `hard`: Jailbreak detection

## Entry points
- `inference.py`: Baseline inference script using OpenAI API.
- `server/app.py`: FastAPI server for OpenEnv compatibility.

## Configuration
Requires `openenv.yaml` to specify environment setup.
