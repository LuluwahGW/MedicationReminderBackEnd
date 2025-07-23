from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {"message":"Hello"}

@app.post('/')
async def post():
    return{
        {'message':'hello from this post'}
    }


@app.get('/items')
async def items():
    return{
        {'message':'list of items'}
    }