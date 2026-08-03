"""In-memory demo conversations for Meta App Review messaging inbox."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

Channel = Literal["whatsapp", "instagram"]
Sender = Literal["customer", "agent"]


@dataclass
class Message:
    id: str
    sender: Sender
    body: str
    sent_at: str  # ISO display-friendly relative or absolute label


@dataclass
class Conversation:
    id: str
    customer_name: str
    channel: Channel
    subject: str
    unread: int
    last_preview: str
    last_at: str
    messages: list[Message] = field(default_factory=list)


def _seed() -> dict[str, Conversation]:
    """Serenity Secret Spa (Dubai) sample threads for App Review."""
    threads = [
        Conversation(
            id="1",
            customer_name="Amina Al Maktoum",
            channel="whatsapp",
            subject="Hammam booking — Friday",
            unread=2,
            last_preview="Do you have availability Friday afternoon for a traditional hammam?",
            last_at="10:42",
            messages=[
                Message("1a", "customer", "Hello, I'm interested in your traditional hammam experience.", "Yesterday 18:12"),
                Message("1b", "agent", "Welcome to Serenity Secret Spa. Our signature hammam is 90 minutes and includes gommage. Which day works for you?", "Yesterday 18:20"),
                Message("1c", "customer", "Do you have availability Friday afternoon for a traditional hammam?", "10:42"),
            ],
        ),
        Conversation(
            id="2",
            customer_name="Sofia Petrov",
            channel="instagram",
            subject="Hair colour + blow dry",
            unread=1,
            last_preview="Can I book a balayage for Saturday morning in DIFC?",
            last_at="09:15",
            messages=[
                Message("2a", "customer", "Hi! Saw your stories — do you do balayage?", "Today 08:50"),
                Message("2b", "agent", "Yes, our colourists offer balayage and gloss. Sessions are typically 2.5–3 hours.", "Today 09:02"),
                Message("2c", "customer", "Can I book a balayage for Saturday morning in DIFC?", "09:15"),
            ],
        ),
        Conversation(
            id="3",
            customer_name="Layla Hassan",
            channel="whatsapp",
            subject="Gel manicure pricing",
            unread=0,
            last_preview="Perfect, see you Thursday at 4pm.",
            last_at="Yesterday",
            messages=[
                Message("3a", "customer", "What's the price for a classic gel manicure?", "Yesterday 14:01"),
                Message("3b", "agent", "Gel manicure is AED 180. We also offer spa manicure with paraffin at AED 250.", "Yesterday 14:08"),
                Message("3c", "customer", "I'll take the gel manicure please — Thursday 4pm if free.", "Yesterday 14:22"),
                Message("3d", "agent", "Confirmed for Thursday 16:00 with Noor. We'll send a Fresha link shortly.", "Yesterday 14:30"),
                Message("3e", "customer", "Perfect, see you Thursday at 4pm.", "Yesterday 14:31"),
            ],
        ),
        Conversation(
            id="4",
            customer_name="Emma Clarke",
            channel="instagram",
            subject="Couples massage packages",
            unread=3,
            last_preview="Is the couples ritual available this weekend?",
            last_at="11:03",
            messages=[
                Message("4a", "customer", "Looking for a couples massage for anniversary — any packages?", "Today 10:40"),
                Message("4b", "customer", "Prefer something with aromatherapy if possible.", "Today 10:41"),
                Message("4c", "customer", "Is the couples ritual available this weekend?", "11:03"),
            ],
        ),
        Conversation(
            id="5",
            customer_name="Noura Al Falasi",
            channel="whatsapp",
            subject="Facial + price list",
            unread=0,
            last_preview="Thank you — I'll book the hydrating facial.",
            last_at="Mon",
            messages=[
                Message("5a", "customer", "Could you share prices for facial treatments?", "Mon 16:00"),
                Message("5b", "agent", "Hydrating facial AED 420 · Deep cleanse AED 380 · Anti-ageing ritual AED 550. All 60–75 min.", "Mon 16:12"),
                Message("5c", "customer", "Thank you — I'll book the hydrating facial.", "Mon 16:45"),
            ],
        ),
        Conversation(
            id="6",
            customer_name="Priya Mehta",
            channel="instagram",
            subject="Nail art / bridal set",
            unread=1,
            last_preview="Do you offer bridal nail sets with custom art?",
            last_at="12:28",
            messages=[
                Message("6a", "customer", "Wedding next month — do you offer bridal nail sets with custom art?", "12:28"),
            ],
        ),
    ]
    return {c.id: c for c in threads}


# Process-lifetime store (resets on deploy/restart — fine for App Review demo)
_STORE: dict[str, Conversation] = _seed()
_msg_counter = 1000


def list_conversations() -> list[Conversation]:
    """Return conversations sorted by unread then id."""
    items = list(_STORE.values())
    items.sort(key=lambda c: (-c.unread, c.id))
    return items


def get_conversation(conv_id: str) -> Conversation | None:
    return _STORE.get(conv_id)


def append_agent_reply(conv_id: str, body: str) -> Conversation | None:
    """Append an agent message and clear unread for the thread."""
    global _msg_counter
    conv = _STORE.get(conv_id)
    if not conv:
        return None
    text = body.strip()
    if not text:
        return conv
    _msg_counter += 1
    now = datetime.now(timezone.utc).strftime("%H:%M")
    msg = Message(id=f"m{_msg_counter}", sender="agent", body=text, sent_at=now)
    conv.messages.append(msg)
    conv.last_preview = text if len(text) <= 80 else text[:77] + "…"
    conv.last_at = now
    conv.unread = 0
    return conv


def reset_demo() -> None:
    """Restore seed data (useful for local testing)."""
    global _STORE, _msg_counter
    _STORE = _seed()
    _msg_counter = 1000


def conversation_as_dict(conv: Conversation) -> dict:
    """Serialize for templates (plain dicts)."""
    return {
        "id": conv.id,
        "customer_name": conv.customer_name,
        "channel": conv.channel,
        "channel_label": "WhatsApp" if conv.channel == "whatsapp" else "Instagram Direct",
        "subject": conv.subject,
        "unread": conv.unread,
        "last_preview": conv.last_preview,
        "last_at": conv.last_at,
        "messages": [
            {
                "id": m.id,
                "sender": m.sender,
                "body": m.body,
                "sent_at": m.sent_at,
            }
            for m in conv.messages
        ],
    }

