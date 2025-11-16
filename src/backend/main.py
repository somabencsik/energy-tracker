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


@app.get("/energies/time")
async def get_energies_time(symbol: str, start_date: str, end_date: str):
    return {"rates": energies.get_energies_from_to(symbol, start_date, end_date)}
