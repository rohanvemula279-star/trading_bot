import os

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok", "message": "AI safety review service is running."}


def main():
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(main(), host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
