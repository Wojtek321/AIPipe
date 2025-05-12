from fastapi import FastAPI
from app.src import pipelines, tasks
import uvicorn

app = FastAPI()

app.include_router(pipelines.router)
app.include_router(tasks.router)


if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
