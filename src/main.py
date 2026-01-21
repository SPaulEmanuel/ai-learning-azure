import sys
import os
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from routers import azure_chatbot
import time
import random
import asyncio

app = FastAPI()

# Include Azure chatbot router
app.include_router(azure_chatbot.router, prefix="/api", tags=["Azure Chatbot"])

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/error")
async def error():
    raise HTTPException(status_code=500, detail="Intentional Error")

@app.get("/load")
async def load():
    latency = random.uniform(1, 5)  # Simulate latency between 1 to 5 seconds
    await asyncio.sleep(latency)  # Simulate latency
    # Simulate CPU load
    start_time = time.time()
    while time.time() - start_time < 2:  # Simulate CPU load for 2 seconds
        pass
    return {"status": "load completed", "latency": latency}