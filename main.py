from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import ADMIN_EMAIL, ADMIN_PASSWORD, WEB_DIR
from .database import Base, SessionLocal, engine
from .models import SCREENING_STEPS, Role, ScreeningStep, User
from .routers import admin, appointments, auth, therapists, video
from .security import hash_password


def ensure_admin():
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(email=ADMIN_EMAIL.lower()).first():
            db.add(
                User(
                    email=ADMIN_EMAIL.lower(),
                    full_name="System Admin",
                    password_hash=hash_password(ADMIN_PASSWORD),
                    role=Role.ADMIN,
                )
            )
            db.commit()
            print(f"[setup] Admin account created: {ADMIN_EMAIL}")
    finally:
        db.close()


def drop_retired_steps():
    """Remove screening steps that are no longer part of the process (e.g. from an older database)."""
    db = SessionLocal()
    try:
        db.query(ScreeningStep).filter(~ScreeningStep.step.in_(SCREENING_STEPS)).delete(
            synchronize_session=False
        )
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_admin()
    drop_retired_steps()
    yield


app = FastAPI(title="Therapist-on-hand", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(therapists.router)
app.include_router(admin.router)
app.include_router(appointments.router)
app.include_router(video.router)


@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok"}


# Serve the web client (also used by the Electron desktop app and the installable mobile PWA)
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
