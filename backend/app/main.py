from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.wallet import router as wallet_router


app = FastAPI(title="Simple Digital Wallet API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(users_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {"message": "Simple Digital Wallet API"}
