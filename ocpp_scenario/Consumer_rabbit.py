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

class ConsumerRabbit:
   

    @staticmethod
    async def consume_messages(connection):
    
        async with connection:
            channel = await connection.channel()
            queue = await channel.get_queue("queue_1")
            queue_close = await channel.get_queue("connection_close")
            async def on_message(message: IncomingMessage):
                async with message.process():
                    raw_message = message.body.decode()
                    #logging.info(f"Received raw message from RabbitMQ: {raw_message}")
                    try:
                        ocpp_message = json.loads(raw_message)
                        
                        if isinstance(ocpp_message, dict):
                            payload = ocpp_message.get("payload")
                            charge_point_id = ocpp_message.get("charge_point_id")
                            if payload and charge_point_id:
                                if isinstance(payload, list):
                                    action = payload[2] 
                                    pay = payload[3]
                            boot = BootNotification()
                            heart = Heartbeat()
                            statusnotif = StatusNotification()
                            authorize=Authorize()
                            start=StartTransaction()
                            stop=StopTransaction
                            meter=MeterValue()
                            #await heart.start()
                            cp = ChargePoint(charge_point_id, None, boot, heart, statusnotif,start,stop,authorize,meter)
                            try:
                                rabbit = Connexion_rabbit()  
                                response = await cp.process_message(action, pay)
                                response_dict = response
                                response_json = Response(charge_point_id, [3, payload[1], response_dict])
                                #logging.info(f"uefbfy{response_json.to_dict()}")
                            except OCPPError as e:
                                response_dict = {
                                    "errorCode": e.args[0], 
                                    "errorDescription": e.args[1] if len(e.args) > 1 else "Unknown error", 
                                    "errorDetails": {} 
                                }
                                #logging.error(f"OCPPError: {response_dict['errorCode']}, Description: {response_dict['errorDescription']}")
                                response_json = Response(charge_point_id, [4, payload[1], response_dict])
                            except Exception as ex:
                                logging.error(f"Unexpected error: {ex}")
                                response_json = Response(charge_point_id, [4, payload[1], {"errorCode": "InternalError", "errorDescription": str(ex)}])
                            await rabbit.publish_message(response_json.to_dict(), "02")
                            #logging.info(f"Response published to RabbitMQ: {response_json}")  
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to decode JSON message: {e}")
            await queue_close.consume(on_message)
            await queue.consume(on_message)
            #logging.info("Consumer started and waiting for messages...")
            await asyncio.Future()
      
                

