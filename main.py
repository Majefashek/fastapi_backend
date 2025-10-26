from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pywebpush import webpush, WebPushException
from pydantic import BaseModel
from typing import Optional
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="FastAPI Push Notification API",
    description="Simple backend to demonstrate Web Push notifications with FastAPI + Next.js",
    version="1.0.0",
)

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")

# Store the subscription in-memory (demo purpose)
subscription_data = None


class Subscription(BaseModel):
    endpoint: str
    keys: dict


@app.get("/", tags=["Health"])
def read_root():
    """Simple health check endpoint."""
    return {"message": "🚀 FastAPI Push Notification Backend running"}


@app.post("/subscribe", tags=["Push Notifications"])
async def subscribe(subscription: Subscription):
    """
    Receive subscription from the frontend (Next.js),
    store it, and send a 'Hello World' push notification.
    """
    global subscription_data
    subscription_data = subscription.dict()
    print("📩 Received subscription:", subscription_data)
    send_push_message("Hello World! 👋")
    return {"message": "Subscription saved & Hello World sent!"}


@app.post("/notify", tags=["Push Notifications"])
def notify(message: Optional[str] = "Manual Notification 🔔"):
    """
    Manually trigger a push notification with a custom message.
    """
    if not subscription_data:
        return {"error": "No subscription available"}
    send_push_message(message)
    return {"message": f"Notification sent: {message}"}


def send_push_message(message: str):
    """Helper function to send a push message."""
    try:
        webpush(
            subscription_info=subscription_data,
            data=json.dumps({
                "title": "FastAPI Notification",
                "body": message,
            }),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": "mailto:admin@example.com"},
        )
        print(f"✅ Push sent: {message}")
    except WebPushException as ex:
        print("❌ Push failed:", repr(ex))
