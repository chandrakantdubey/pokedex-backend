from fastapi import FastAPI
from .database import engine, Base
from .routers import pokemon, auth, users, game, world, shop

Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Pokedex API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pokemon.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(game.router)
app.include_router(world.router)
app.include_router(shop.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Pokedex API"}
