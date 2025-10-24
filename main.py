from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from livekit import api
from livekit.agents import Agent, AgentSession, JobContext, RoomInputOptions, WorkerOptions, cli
from livekit.plugins import google, tavus, noise_cancellation, silero
#from livekit.plugins import google

import multiprocessing
from dotenv import load_dotenv
import os
import uvicorn




from prompt import AGENT_PROMPT, SESSION_PROMPT
from tools import (
    get_system_status,
    get_system_overview,
    get_current_operating_conditions,
    get_energy_performance,
    get_pv_forecast,
    get_component_data_sheet,
)

load_dotenv()

# FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],#["http://localhost:5173"],  # Allow requests from your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_token")
async def token(request: Request):
    """Create a LiveKit token for the user."""
    room_name = request.query_params.get("room_name")
    identity = request.query_params.get("identity")
    print(f"Generating token for room: {room_name}, identity: {identity}")
    if not room_name or not identity:
        return JSONResponse({"error": "room_name and identity are required"}, status_code=400)

    token = (
        api.AccessToken(os.environ.get("LIVEKIT_API_KEY"), os.environ.get("LIVEKIT_API_SECRET"))
        .with_identity(identity)
        .with_name(identity)
        .with_grants(api.VideoGrants(room_join=True, room=room_name))
        .to_jwt()
    )
    # print("Generated token:", token)

    return JSONResponse({"token": token, "url": os.environ.get("LIVEKIT_URL")})


# LiveKit Agent
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_PROMPT,
            tools=[
                get_system_status,
                get_system_overview,
                get_current_operating_conditions,
                get_energy_performance,
                get_pv_forecast,
                get_component_data_sheet,
            ],
        )

async def entrypoint(ctx: JobContext):
    """Entrypoint for the LiveKit agent."""
    print("Starting agent session...")
    await ctx.connect()
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Kore",
            temperature=0.8,
            instructions="You are a helpful assistant",
        ),
    )

    assistant = Assistant()
    import json
    async def write_transcript():
        filename = "summary.json"
        with open(filename, 'w') as f:
            json.dump(session.history.to_dict(), f, indent=2)
        print(f"Transcript for {ctx.room.name} saved to {filename}")

    ctx.add_shutdown_callback(write_transcript)

    tavus_avatar = tavus.AvatarSession(
        persona_id=os.environ.get("TAVUS_PERSONA_ID"),
        replica_id=os.environ.get("TAVUS_REPLICA_ID"),
    )
    await tavus_avatar.start(session, room=ctx.room)

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
            audio_enabled=True,
        ),
    )

    print(f"Agent joined room: {ctx.room.name}")


    await session.generate_reply(instructions=SESSION_PROMPT)


def run_agent():
    print("Starting LiveKit agent...")
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

# if __name__ == "__main__":
#     agent_process = multiprocessing.Process(target=run_agent)
#     agent_process.start()

#     uvicorn.run(app, host="0.0.0.0", port=8000)

import asyncio

import httpx
import base64

import httpx
from livekit import api

import httpx
from livekit import api

async def launch_agent_job():
    livekit_url = os.environ["LIVEKIT_URL"].replace("wss://", "https://")
    api_key = os.environ["LIVEKIT_API_KEY"]
    api_secret = os.environ["LIVEKIT_API_SECRET"]

    # Generate proper Bearer token with both room and identity
    token = (
        api.AccessToken(api_key, api_secret)
        .with_identity("agent-backend")  # ✅ required
        .with_grants(api.VideoGrants(room_join=True, room="olivia-room"))
        .to_jwt()
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = {
        "name": "tavus-agent",
        "room": "olivia-room",
        "agentInfo": {"entrypoint": "entrypoint"},
    }

    async with httpx.AsyncClient() as client:
        print("🚀 Launching agent job for room...")
        resp = await client.post(f"{livekit_url}/api/v1/jobs", headers=headers, json=data)
        print("✅ Agent job response:", resp.status_code, resp.text)


if __name__ == "__main__":
    agent_process = multiprocessing.Process(target=run_agent)
    agent_process.start()

    # Launch job after backend starts
    asyncio.run(launch_agent_job())

    uvicorn.run(app, host="0.0.0.0", port=8000)

