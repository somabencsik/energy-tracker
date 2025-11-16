from fastapi import FastAPI

from database import energies


energies.init_database()

app = FastAPI()

@app.get("/")
async def get_root():
    return {"Hello": "World"}


@app.get("/energies")
async def get_energies():
    return {"energies": energies.get_energies()}
