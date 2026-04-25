from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.consult import router as consult_router
from app.routers.market_prices import router as market_prices_router

app = FastAPI(title="Tio Cumbana", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(consult_router)
app.include_router(market_prices_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
