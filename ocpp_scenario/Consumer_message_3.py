import asyncio
import logging
import aio_pika
import websockets
import json
from aio_pika import IncomingMessage
from ocpp_scenario.ChargePoint import ChargePoint
from ocpp_scenario.Bootnotification import BootNotification
from ocpp_scenario.Heartbeat import Heartbeat
from ocpp_scenario.StatusNotification import StatusNotification
from ocpp_scenario.Authorize import Authorize
from ocpp_scenario.StartTransaction import StartTransaction
from ocpp_scenario.StopTransaction import StopTransaction
from ocpp_scenario.Connexion_rabbit import Connexion_rabbit
from ocpp_scenario.MeterValue import MeterValue
from ocpp_scenario.Response import Response
from ocpp.exceptions import OCPPError

class ConsumerMessage:
    @staticmethod
    async def consume_messages(connection):
    
        async with connection:
            channel = await connection.channel()
            queue = await channel.get_queue("message_3")
            async def on_message(message: IncomingMessage):
                async with message.process():
                    raw_message = message.body.decode()
                    logging.info(f"Received raw message from RabbitMQ: {raw_message}")
                    try:
                        ocpp_message = json.loads(raw_message)
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to decode JSON message: {e}")
            await queue.consume(on_message)
            #logging.info("Consumer started and waiting for messages...")
            await asyncio.Future()
      
                

