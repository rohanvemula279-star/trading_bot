"""
FastAPI server for the AI Safety Review Environment.

Exposes the environment via OpenEnv HTTP/WebSocket endpoints.
"""

from fastapi import FastAPI
from openenv.core.env_server import create_app
from environment import SafetyReviewEnv
from models import SafetyAction, SafetyObservation

# Create the OpenEnv-compliant app
app = create_app(
    SafetyReviewEnv,
    action_cls=SafetyAction,
    observation_cls=SafetyObservation,
)

@app.get("/")
async def root():
    return {
        "status": "OpenEnv SafetyReviewEnv is running",
        "routes": ["/health", "/docs", "/metadata", "/mcp", "/ws"],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
