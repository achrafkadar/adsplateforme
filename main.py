"""Minimal Wenov Ads Platform surface for Meta App Review."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import demo_inbox

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


def require_auth(request: Request) -> RedirectResponse | None:
    """Return a redirect to login when the session is not authenticated."""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    return None


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
    denied = require_auth(request)
    if denied:
        return denied
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"title": "Dashboard", "user": request.session.get("email")},
    )


@app.get("/inbox", response_class=HTMLResponse, response_model=None)
async def inbox_list(request: Request) -> Response:
    denied = require_auth(request)
    if denied:
        return denied
    conversations = [
        demo_inbox.conversation_as_dict(c) for c in demo_inbox.list_conversations()
    ]
    return templates.TemplateResponse(
        request,
        "inbox.html",
        {
            "title": "Messaging inbox",
            "user": request.session.get("email"),
            "conversations": conversations,
        },
    )


@app.get("/inbox/{conv_id}", response_class=HTMLResponse, response_model=None)
async def inbox_thread(request: Request, conv_id: str) -> Response:
    denied = require_auth(request)
    if denied:
        return denied
    conv = demo_inbox.get_conversation(conv_id)
    if not conv:
        return RedirectResponse(url="/inbox", status_code=303)
    return templates.TemplateResponse(
        request,
        "inbox_thread.html",
        {
            "title": conv.customer_name,
            "user": request.session.get("email"),
            "conversation": demo_inbox.conversation_as_dict(conv),
        },
    )


@app.post("/inbox/{conv_id}/reply", response_model=None)
async def inbox_reply(
    request: Request,
    conv_id: str,
    body: str = Form(...),
) -> Response:
    denied = require_auth(request)
    if denied:
        return denied
    if not demo_inbox.get_conversation(conv_id):
        return RedirectResponse(url="/inbox", status_code=303)
    demo_inbox.append_agent_reply(conv_id, body)
    return RedirectResponse(url=f"/inbox/{conv_id}", status_code=303)


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
