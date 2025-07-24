from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel




app = FastAPI()



class ModelName(str , Enum):
    alexnet ="alexnet"
    resnet = "resnet"
    lenet = "lenet"

class Items(BaseModel):
    name : str
    description : str | None = None
    price : float 
    tax : float | None = None




@app.get('/')
async def root():
    return {"message":"Hello"}

@app.post('/items') 
async def create_item(item : Items) : #-> item
    return item
    



@app.get('/items/{item_id}')
async def read_items(item_id :int):
    return {'item_id':item_id}

@app.get('/users')
async def read_users():
    return["lulu","gw"]
   

@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return{"model_name": model_name, "message" :"Deep Learning FTW"}
    if model_name is ModelName.lenet:
        return{"model_name":model_name, "message":"idk wtf is going on"}
    if model_name is ModelName.resnet:
        return{"model_name":model_name, "message":"RELEASE ME!!!!"}
