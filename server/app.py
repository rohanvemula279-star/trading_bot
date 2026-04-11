"""OpenEnv server entrypoint.

`openenv validate` expects a repo-level server entrypoint exposed via
`[project.scripts] server`.
"""

import os

from openenv.core.env_server import create_app

from environment import SafetyReviewEnv
from models import SafetyAction, SafetyObservation

app = create_app(
    SafetyReviewEnv,
    action_cls=SafetyAction,
    observation_cls=SafetyObservation,
)

@app.get("/")
def root():
    """Root endpoint returning service status and available routes."""
    routes = [{"path": route.path, "name": route.name} for route in app.routes]
    return {
        "status": "ok", 
        "message": "AI safety review service is running.",
        "routes": routes
    }

def main():
    """Main entrypoint for the OpenEnv FastAPI server."""
    import uvicorn
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

