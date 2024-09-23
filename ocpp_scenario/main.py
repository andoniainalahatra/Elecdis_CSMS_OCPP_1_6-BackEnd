import os
import asyncio
import logging
import websockets
import ssl
from fastapi import FastAPI
from ocpp_scenario.Connexion_web import Connexion
from ocpp_scenario.Connexion_rabbit import Connexion_rabbit

logging.basicConfig(level=logging.INFO)
DATABASE_URL = os.getenv("DATABASE_URL")

# Define the WebSocket server startup function
async def start_websocket_server():
    try:
        #ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        #ssl_context.load_cert_chain(certfile="./certificate_key/cert.pem", keyfile="./certificate_key/key.pem")
        connexion = Connexion()
        server = await websockets.serve(
            connexion.on_connect,
            '0.0.0.0',
            9001,
            #ssl=ssl_context,
            subprotocols=['ocpp1.6']
        )
        logging.info("Serveur WebSocket démarré sur ws://0.0.0.0:9001")
        await server.wait_closed()
    except Exception as e:
        logging.error("Erreur lors du démarrage du serveur : %s", str(e))

# Function to run RabbitMQ configuration
async def run_rabbit_config():
    rabbit = Connexion_rabbit()
    await rabbit.config_rabbit()

# Define a function that starts both the WebSocket server and RabbitMQ configuration
async def main():
    # Run both tasks concurrently
    await asyncio.gather(
        start_websocket_server(),
        run_rabbit_config()
    )

if __name__ == "__main__":
    # Run the asyncio event loop
    asyncio.run(main())
