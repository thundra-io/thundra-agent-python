from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/{param}")
def root(param: int):
    return JSONResponse({ "hello_world": param})


@app.get("/error")
def error():
    raise RuntimeError('Test Error')
