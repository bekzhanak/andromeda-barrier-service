from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel, IPvAnyAddress
import socket
import os

app = FastAPI()

PORT = 5000  # Default port for ESP barrier devices
API_KEY = os.getenv("API_KEY")  # Backend-provided key for auth

# Command mapping: human-readable → device instruction
COMMAND_MAP = {
    "open": 1,
    "close": 2
}


class BarrierCommand(BaseModel):
    ip: IPvAnyAddress
    command: str  # "open" or "close"


def send_to_esp(ip: str, message: int) -> str:
    """
    Connect to ESP and send command via TCP socket.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((ip, PORT))
            s.sendall(str(message).encode())
            response = s.recv(1024)
            return response.decode().strip()
    except Exception as e:
        raise RuntimeError(f"Failed to communicate with ESP at {ip}: {e}")


@app.post("/barrier/control/")
async def control_barrier(command: BarrierCommand, request: Request):
    """
    Receives a command to control the barrier (open/close) at the specified IP.
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer ") or auth_header.split()[1] != API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")

    if command.command not in COMMAND_MAP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid command. Allowed: {list(COMMAND_MAP.keys())}"
        )

    message_code = COMMAND_MAP[command.command]

    print(f"Running the command {command.command} on {command.ip}")

    try:
        response = send_to_esp(str(command.ip), message_code)
        return {
            "status": "success",
            "command_sent": command.command,
            "device_response": response
        }
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
