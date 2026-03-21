from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.network.router import router as network_router
from app.modules.platform.router import router as platform_router
from app.modules.coach.router import router as coach_router
from app.modules.safety.router import router as safety_router

app = FastAPI(title="RAIL-INTELLIGENCE")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(network_router, prefix="/network", tags=["Network"])
app.include_router(platform_router, prefix="/platform", tags=["Platform"])
app.include_router(coach_router, prefix="/coach", tags=["Coach"])
app.include_router(safety_router, prefix="/safety", tags=["Safety"])


@app.get("/")
def root():
    return {"message": "RAIL-INTELLIGENCE API running"}
