import asyncio
import websockets
import json
from websockets.exceptions import ConnectionClosedError
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
import logging
from ocpp_scenario.Connexion_rabbit import Connexion_rabbit
from ocpp_scenario.Consumer_rabbit import ConsumerRabbit
from ocpp_scenario.Consumer_rabbit2 import ConsumerRabbit2
from ocpp_scenario.Response import Response
from typing import Dict

logging.basicConfig(level=logging.INFO)
class Connexion:
    connections={}    
    # def __init__(self):
    #     self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}

    # async def get_connection(self, charge_point_id: str) -> websockets.WebSocketServerProtocol:
    #     websocket = self.connections.get(charge_point_id)
    #     if websocket is None:
    #         logging.error(f"No WebSocket connection found for charge_point_id: {charge_point_id}")
    #     return websocket

    # async def set_connection(self, charge_point_id: str, websocket: websockets.WebSocketServerProtocol):
    #     self.connections[charge_point_id] = websocket
    #     logging.info(f"WebSocket connection set for charge_point_id: {charge_point_id}")

    # def show_connections(self):
    #     if self.connections:
    #         logging.info("Current WebSocket connections:")
    #         for charge_point_id, websocket in self.connections.items():
    #             logging.info(f"Charge Point ID: {charge_point_id}, WebSocket: {websocket}")
    #     else:
    #         logging.info("No WebSocket connections available.")
    @staticmethod
    async def receive_messages(websocket, message_queue,failed_message_queue, rabbit_mq,charge_point_id):
        try:
            while True:
                # Recevoir un message du WebSocket
                message1 = await websocket.recv()
                message = json.loads(message1)
                val=Response(charge_point_id,message)
                logging.info(f"Message reçu brut : {message1}")
                try:
                    if message[0] == 2 :
                        await message_queue.put(val.to_dict())
                except (json.JSONDecodeError, IndexError) as e:
                    logging.error(f"Erreur de traitement du message : {e}")
                try:
                    await websocket.ping()
                except Exception as e:
                    await failed_message_queue.put(val.to_dict())
                    break              

        except ConnectionClosedError:
            logging.info("WebSocket connection closed")
        except Exception as e:
            logging.error(f"Error during message reception: {e}")
    @staticmethod
    async def process_messages(message_queue,failed_message_queue,rabbit_mq):
        while True:
            if not failed_message_queue.empty():
                message = await failed_message_queue.get()
                await rabbit_mq.publish_message(message, "03")
            else:
                message = await message_queue.get()
                await rabbit_mq.publish_message(message, "01")
            
    @staticmethod       
    async def on_connect(websocket,path):
        try:
            charge_point_id = path.strip('/')
            Connexion.connections[charge_point_id]=websocket
            rabbitmq_publisher = Connexion_rabbit()
            connection=await rabbitmq_publisher.get_rabbit_connection()
            message_queue = asyncio.Queue()
            failed_message_queue = asyncio.Queue()
            await asyncio.gather(
                Connexion.receive_messages(websocket, message_queue,failed_message_queue,rabbitmq_publisher,charge_point_id),
                Connexion.process_messages(message_queue,failed_message_queue, rabbitmq_publisher),
                ConsumerRabbit.consume_messages(connection),
                ConsumerRabbit2.consume_messages(connection)
               
            )
        except Exception as e:
            logging.error(f"Error during WebSocket connection setup: {e}")
        
    @staticmethod 
    async def send_messages(charge_point_id: str, payload: dict):
        try:
            websocket = Connexion.connections.get(charge_point_id)
            if websocket is None or websocket.closed:
                logging.error(f"Cannot send message, no WebSocket connection for {charge_point_id}")
                return
            
            payload = json.dumps(payload) if isinstance(payload, (dict, list)) else str(payload)
            logging.info(f"Payload type after conversion: {type(payload)}")
            await websocket.send(payload)
            print(f"Sent message to {charge_point_id}: {payload}")

        except ConnectionClosedError:
            logging.info("WebSocket connection closed")
        except Exception as e:
            logging.error(f"Error during message reception: {e}")