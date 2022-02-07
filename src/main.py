import asyncio
from fastapi import FastAPI, Request, Depends

import supervisely as sly
# from supervisely.fastapi_helpers import create_supervisely_app, shutdown, get_app_data_dir, Jinja2Templates
# from supervisely.fastapi_helpers import StateJson, DataJson, LastStateJson, ContextJson



import names
import time
from asgiref.sync import async_to_sync

import os
# import sys
# from pathlib import Path
# app (repo) root directory #@TODO: not working
# app_dir = os.path.abspath(Path(sys.argv[0]).parents[1])
# sys.path.append(app_dir)
# print(f"App root directory: {app_dir}")

#@TODO: change both state and data and return them in response
#@TODO: long method without await and then stop task manually from client
#@TODO: umar zoom-to-figure - use in clicker app?
#@TODO: custom vue.js method for python devs (example)
#@TODO: apps 2.0 apps examples (aka aed)
#@TODO: global-dependencies max
#@TODO: use state/data xorrectly in our all official examples
#@TODO: tiny dockerimage 
#@TODO: test integration into panel


# init state and data (singletons)
sly.app.LastStateJson({ "name": "abc", "counter": 0})
sly.app.DataJson({"max": 123, "counter": 0})


app = FastAPI()
sly_app = sly.app.fastapi.create()
app.mount("/sly", sly_app)

templates = sly.app.fastapi.Jinja2Templates(directory="templates")



# sly.app.fastapi.create()
# sly.app.fastapi.shutdown()
# sly.app.fastapi.Jinja2Templates
# sly.app.get_data_dir()
# sly.app.StateJson
# sly.app.DataJson 
# sly.app.LastStateJson 
# sly.app.ContextJson


@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

# #@TODO: hide functionality -> return changes 
# @app.post("/generate")
# async def generate(request: Request, state: StateJson = Depends(StateJson.from_request)):
#     state["name"] = names.get_first_name()
#     return state.get_changes()  # return state changes to client


@app.post("/generate-ws")
async def generate_ws(request: Request, state: StateJson = Depends(StateJson.from_request)):
    state["name"] = names.get_first_name()
    await state.synchronize_changes()  # use websocket to send state changes to client


@app.post("/sync-generate")
def sync_generate(request: Request, state: StateJson = Depends(StateJson.from_request)):
    state["name"] = names.get_first_name()
    time.sleep(50)
    async_to_sync(state.synchronize_changes)()


@app.post("/do-then-shutdown")
async def do_then_shutdown(request: Request, state: StateJson = Depends(StateJson.from_request)):
    print("do something here and then manual shutdown")
    sly.app.fastapi.shutdown()


@app.post("/count-state")
async def count_state(request: Request, state: StateJson = Depends(StateJson.from_request)):
    for i in range(10):
        await asyncio.sleep(0.5)
        state["counter"] = i
        await state.synchronize_changes()


@app.post("/count-data")
async def count_state(request: Request, state: StateJson = Depends(StateJson.from_request)):
    data = sly.app.DataJson() # singleton
    for i in range(10):
        await asyncio.sleep(0.5)
        data["counter"] = i
        await data.synchronize_changes()


@app.on_event("startup")
def startup_event():
    print("startup_event --- init something before server starts")
    sly.app.get_data_dir()
    


@app.on_event("shutdown")
def shutdown_event():
    print("shutdown_event --- do something before server shutdowns")
