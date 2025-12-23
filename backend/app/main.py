from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import forms, submissions, agents, login
from app.core.config import settings

app = FastAPI(title="Smart Form Automation API", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "backend"}

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Form Automation API"}

print(f"DEBUG: API Prefix is '{settings.API_V1_STR}'")
print(f"DEBUG: Registering routers...")
app.include_router(forms.router, prefix=f"{settings.API_V1_STR}/forms", tags=["forms"])
app.include_router(submissions.router, prefix=f"{settings.API_V1_STR}", tags=["submissions"])
app.include_router(agents.router, prefix=f"{settings.API_V1_STR}/agents", tags=["agents"])
app.include_router(login.router, prefix=f"{settings.API_V1_STR}", tags=["login"])
print(f"DEBUG: Forms routes: {len(forms.router.routes)}")
print(f"DEBUG: Agents routes: {len(agents.router.routes)}")
