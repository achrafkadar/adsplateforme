"""Minimal Wenov Ads Platform surface for Meta App Review."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

BASE_DIR = Path(__file__).resolve().parent

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "review@wenov.ca")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-only-change-me")

app = FastAPI(title="Wenov Ads Platform", docs_url=None, redoc_url=None)
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="wenov_session",
    same_site="lax",
    https_only=os.getenv("RENDER", "").lower() == "true",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def is_authenticated(request: Request) -> bool:
    """Return True when the session has a logged-in user."""
    return bool(request.session.get("authenticated"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {"title": "Wenov Ads Platform", "user": request.session.get("email")},
    )


@app.get("/login", response_class=HTMLResponse, response_model=None)
async def login_page(request: Request) -> Response:
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Sign in", "error": None, "user": None},
    )


@app.post("/login", response_model=None)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
) -> Response:
    if email.strip().lower() == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD:
        request.session["authenticated"] = True
        request.session["email"] = email.strip().lower()
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Sign in", "error": "Invalid email or password.", "user": None},
        status_code=401,
    )


@app.post("/logout")
async def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse, response_model=None)
async def dashboard(request: Request) -> Response:
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"title": "Dashboard", "user": request.session.get("email")},
    )


@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "privacy.html",
        {"title": "Privacy Policy", "user": request.session.get("email")},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
