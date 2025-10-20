import asyncio
import os
import json # Optional: for structured data
from websockets.server import serve

# A set to keep track of all connected clients (Android app, ESP32, etc.)
CONNECTED_CLIENTS = set()

async def handler(websocket):
    """
    This function is called for each new WebSocket connection.
    """
    # Add the new client to our set of connected clients
    CONNECTED_CLIENTS.add(websocket)
    print(f"New client connected: {websocket.remote_address}")
    
    try:
        # This loop runs as long as the connection is open
        async for message in websocket:
            print(f"Received message: {message}")
            
            # --- BROADCAST LOGIC ---
            # Send the received message to all other connected clients.
            # This is how the Android app will get the ESP32's data.
            clients_to_send = [client for client in CONNECTED_CLIENTS if client != websocket]
            
            # Use asyncio.gather to send messages concurrently
            if clients_to_send:
                await asyncio.gather(
                    *[client.send(message) for client in clients_to_send]
                )

    finally:
        # This code runs when the client disconnects
        CONNECTED_CLIENTS.remove(websocket)
        print(f"Client disconnected: {websocket.remote_address}")

async def main():
    """
    The main function to start the server.
    """
    # 1. HOST: Listen on 0.0.0.0 to accept connections from Render's router
    host = "0.0.0.0"

    # 2. PORT: Get the port from Render's environment variable, default to 8080 for local testing
    port = int(os.environ.get("PORT", 8080))
    
    print(f"Starting WebSocket server on {host}:{port}")

    # Start the WebSocket server
    async with serve(handler, host, port):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
