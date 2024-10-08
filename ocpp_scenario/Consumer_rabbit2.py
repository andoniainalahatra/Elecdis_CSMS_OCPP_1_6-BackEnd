import asyncio
import logging
import aio_pika
import websockets
import json
from aio_pika import IncomingMessage

from websockets.exceptions import WebSocketException




class ConsumerRabbit2:
    async def consume_messages(connection):
        from ocpp_scenario.Connexion_web import Connexion
        async with connection:
            channel = await connection.channel()        
            queue = await channel.get_queue("queue_2")
            async def on_message(message: IncomingMessage):
                async with message.process():
                    raw_message = message.body.decode()
                   
                    try:
                        ocpp_message = json.loads(raw_message)
                        if isinstance(ocpp_message, dict):
                            payload = ocpp_message.get("payload")
                            charge_point_id = ocpp_message.get("charge_point_id")
                            connexion=Connexion()
                            #await asyncio.sleep(2)
                            await connexion.send_messages(charge_point_id,payload)
                            logging.info(f"CP <= CSMS{payload}")
                        
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to decode JSON message: {e}")
                    except WebSocketException as e:
                            logging.error(f"WebSocket error: {type(e).__name__} - {str(e)}")
                    except ConnectionError as e:
                            logging.error(f"Connection error: {type(e).__name__} - {str(e)}")
                    except TimeoutError as e:
                            logging.error(f"Timeout error: {type(e).__name__} - {str(e)}")
                    except Exception as e:
                            # Capturer toute autre exception non spécifiée
                            logging.error(f"Unexpected error: {type(e).__name__} - {str(e)}")

            await queue.consume(on_message)
            #logging.info("Consumer started and waiting for messages...")
            await asyncio.Future()  # Run indefinitely
            
