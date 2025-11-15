from fastapi import FastAPI

from database import energies

app = FastAPI()

engine = energies.get_engine()

@app.get("/")
async def get_root():
    return {"Hello": "World"}
