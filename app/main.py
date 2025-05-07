from fastapi import FastAPI
from routers import pipelines, tasks, utils
import uvicorn

app = FastAPI()


app.include_router(pipelines.router)
app.include_router(tasks.router)
app.include_router(utils.router)


@app.get("/")
def root():
    return {"message": "root"}


if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
