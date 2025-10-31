from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pywebpush import webpush, WebPushException
from pydantic import BaseModel
from typing import Optional
import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("uvicorn")


app = FastAPI(
    title="FastAPI Push Notification API",
    description="Simple backend to demonstrate Web Push notifications with FastAPI + Next.js",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")

subscription_data = None

# --- Models ---
# This ensures the 'keys' object has both 'p256dh' and 'auth'
class SubscriptionKeys(BaseModel):
    p256dh: str
    auth: str

class Subscription(BaseModel):
    endpoint: str
    keys: SubscriptionKeys

# --- Endpoints ---

@app.get("/", tags=["Health"])
def read_root():
    logger.info("Health check endpoint '/' was called")
    return {"message": "🚀 FastAPI Push Notification Backend running"}

@app.get("/test-500", tags=["Health"])
def test_500_error():
    logger.warning("💥 Triggering a 500 error now...")
    result = 1 / 0
    return {"message": "You will not see this"}


@app.post("/subscribe", tags=["Push Notifications"])
async def subscribe(subscription: Subscription): # Pydantic validates the data here
    global subscription_data
    subscription_data = subscription.dict() 
    
    # -------------------------------------------------------------------
    # 💡 MODIFIED LOG: This now prints the ENTIRE subscription object
    # -------------------------------------------------------------------
    logger.info(f"📩 Received full subscription object: {subscription_data}")
    
    send_push_message("Hello World! 👋")
    return {"message": "Subscription saved & Hello World sent!"}


@app.post("/notify", tags=["Push Notifications"])
def notify(message: Optional[str] = "Manual Notification 🔔"):
    if not subscription_data:
        logger.warning("Tried to notify, but no subscription is available.")
        return {"error": "No subscription available"}
        
    logger.info(f"Triggering manual notification: {message}")
    send_push_message(message)
    return {"message": f"Notification sent: {message}"}

# --- Helper Function ---

def send_push_message(message: str):
    if not subscription_data:
        logger.error("❌ send_push_message called with no subscription_data")
        return

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
        logger.info(f"✅ Push sent: {message}")
        
    except WebPushException as ex:
        logger.error(f"❌ Push failed: {repr(ex)}", exc_info=True)
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: {repr(e)}", exc_info=True)