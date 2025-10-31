from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pywebpush import webpush, WebPushException
from pydantic import BaseModel
from typing import Optional
import os
import json
import logging  # Import the logging module
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------------------------
# 💡 CONFIGURING THE LOGGER
# This is the most important part. We get the "uvicorn" logger
# so all our logs go to the same stream as the web server.
# This fixes the "no logs" problem.
# -------------------------------------------------------------------
logger = logging.getLogger("uvicorn")


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
    logger.info("Health check endpoint '/' was called")
    return {"message": "🚀 FastAPI Push Notification Backend running"}


# -------------------------------------------------------------------
# 💡 NEW ENDPOINT TO TEST 500 ERRORS
# -------------------------------------------------------------------
@app.get("/test-500", tags=["Health"])
def test_500_error():
    """
    This endpoint deliberately raises an unhandled exception (500 error)
    to prove that it will be logged.
    """
    logger.warning("💥 Triggering a 500 error now...")
    # This will cause a ZeroDivisionError, which is an unhandled 500 error
    result = 1 / 0
    return {"message": "You will not see this"}


@app.post("/subscribe", tags=["Push Notifications"])
async def subscribe(subscription: Subscription):
    """
    Receive subscription from the frontend (Next.js),
    store it, and send a 'Hello World' push notification.
    """
    global subscription_data
    subscription_data = subscription.dict()
    
    # Use logger.info() instead of print()
    logger.info(f"📩 Received subscription: {subscription_data['endpoint']}")
    
    send_push_message("Hello World! 👋")
    return {"message": "Subscription saved & Hello World sent!"}


@app.post("/notify", tags=["Push Notifications"])
def notify(message: Optional[str] = "Manual Notification 🔔"):
    """
    Manually trigger a push notification with a custom message.
    """
    if not subscription_data:
        # Use logger.warning() for non-critical issues
        logger.warning("Tried to notify, but no subscription is available.")
        return {"error": "No subscription available"}
        
    logger.info(f"Triggering manual notification: {message}")
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
            vapid_claims={"sub": "mailto:abdullahishuaibumaje@gmail.com"},
        )
        # Use logger.info() for success messages
        logger.info(f"✅ Push sent: {message}")
        
    except WebPushException as ex:
        # Use logger.error() for exceptions.
        # exc_info=True will automatically include the full stack trace.
        logger.error(f"❌ Push failed: {repr(ex)}", exc_info=True)