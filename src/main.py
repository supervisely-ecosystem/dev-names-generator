import asyncio
import os
import sys
from pathlib import Path

from fastapi import FastAPI, Request, Depends

import supervisely as sly
from supervisely.fastapi_helpers import get_subapp, shutdown, Jinja2Templates
from supervisely.fastapi_helpers import StateJson, DataJson, LastStateJson, ContextJson

#@TODO: class or instance method cls._field from request, etc...
import names
import time
from asgiref.sync import async_to_sync

# app (repo) root directory #@TODO: not working
# app_dir = os.path.abspath(Path(sys.argv[0]).parents[1])
# sys.path.append(app_dir)
# print(f"App root directory: {app_dir}")

# init state and data (singletons)
LastStateJson({ "name": "abc", "counter": 0})
DataJson({"max": 123})

app = FastAPI()
sly_app = get_subapp()
app.mount("/sly", sly_app)

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post("/sync-generate")
def sync_generate(request: Request):
    # example how to execute ASYNC methods in SYNC function
    json_body = async_to_sync(request.json)()
    time.sleep(1.5)
    # state["name"] = names.get_first_name()
    # async_to_sync(state.synchronize_changes())


@app.post("/generate")
async def generate(request: Request, state: StateJson = Depends(StateJson.from_request)):
    s1 = await request.json()
    s2 = await request.json()
    s3 = await request.json()
    state["name"] = names.get_first_name()
    return state.get_changes()


@app.post("/generate-ws")
async def generate_ws(request: Request, state: StateJson = Depends(StateJson.from_request)):
    state["name"] = names.get_first_name()
    await state.synchronize_changes() # using websocket


@app.post("/do-then-shutdown")
async def do_then_shutdown(request: Request, state: StateJson = Depends(StateJson.from_request)):
    print("do something here and then manual shutdown")
    shutdown(app)
    # or 
    # shutdown(request.app)


@app.post("/count")
async def count(request: Request, state: StateJson = Depends(StateJson.from_request)):
    for i in range(10):
        asyncio.sleep(1)
        state["counter"] = i
        await state.synchronize_changes()


@app.on_event("startup")
def startup_event():
    print("startup_event --- init something before server starts")


@app.on_event("shutdown")
def shutdown_event():
    print("shutdown_event --- do something before server shutdowns")
