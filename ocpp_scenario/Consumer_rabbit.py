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
                                logging.info(f"uefbfy{response_json.to_dict()}")
                            except OCPPError as e:
                                response_dict = {
                                    "errorCode": e.args[0],  # Utiliser le premier argument comme code d'erreur
                                    "errorDescription": e.args[1] if len(e.args) > 1 else "Unknown error",  # Description de l'erreur
                                    "errorDetails": {}  # Ajouter des détails supplémentaires si nécessaires
                                }
                                logging.error(f"OCPPError: {response_dict['errorCode']}, Description: {response_dict['errorDescription']}")
                                response_json = Response(charge_point_id, [4, payload[1], response_dict])
                            except Exception as ex:
                                logging.error(f"Unexpected error: {ex}")
                                response_json = Response(charge_point_id, [4, payload[1], {"errorCode": "InternalError", "errorDescription": str(ex)}])
                            await rabbit.publish_message(response_json.to_dict(), "02")
                            logging.info(f"Response published to RabbitMQ: {response_json}")  
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to decode JSON message: {e}")
            await queue_close.consume(on_message)
            await queue.consume(on_message)
            logging.info("Consumer started and waiting for messages...")
            await asyncio.Future()
      
                

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     asyncio.run(ConsumerRabbit.consume_messages())



# import asyncio
# import logging
# import aio_pika
# import json
# from aio_pika import IncomingMessage, Message
# from ocpp.v16 import call_result
# from ocpp_scenario.Bootnotification import BootNotification
# from ocpp_scenario.Heartbeat import Heartbeat
# from ocpp_scenario.StatusNotification import StatusNotification
# from ocpp_scenario.Connexion_rabbit import Connexion_rabbit

# class ConsumerRabbit:
#     @staticmethod
#     async def get_rabbit_connection():
#         connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
#         logging.info("Connection to RabbitMQ established")
#         return connection
#     async def consume_messages():
#         connection = await ConsumerRabbit.get_rabbit_connection()
#         async with connection:
#             channel = await connection.channel()
#             queue = await channel.get_queue("queue_1")

#             async def on_message(message: IncomingMessage):
#                 async with message.process():
#                     raw_message = message.body.decode()
#                     logging.info(f"Received raw message from RabbitMQ: {raw_message}")

#                     try:
#                         # Charger le message JSON
#                         ocpp_message = json.loads(raw_message)

#                         # Initialiser les scénarios
#                         boot = BootNotification()
#                         heart = Heartbeat()
#                         statusnotif = StatusNotification()

                        
#                         action = ocpp_message[2]
#                         payload = ocpp_message[3]

#                         # Identifier et traiter le type de message OCPP
#                         if action == "BootNotification":
#                             response = await boot.on_boot_notification(
#                                 payload["chargePointVendor"],
#                                 payload["chargePointModel"]
#                             )
#                             logging.info(f"Processed BootNotification with response: {response}")

#                         elif action == "Heartbeat":
#                             response = await heart.on_heartbeat()
#                             logging.info(f"Processed Heartbeat with response: {response}")

#                         elif action == "StatusNotification":
#                             response = await statusnotif.on_statusnotification(
#                                 payload["connectorId"],
#                                 payload["status"],
#                                 payload["errorCode"]
#                             )
#                             logging.info(f"Processed StatusNotification with response: {response}")

#                         else:
#                             logging.info("Message type is not recognized, skipping processing.")
#                             response = None

#                         # Publier la réponse sur RabbitMQ
#                         if response:
#                             rabbit=Connexion_rabbit()
#                             response_dict = response

#                             # Convertir la réponse en JSON
#                             response_json = [3, ocpp_message[1], response_dict]
#                             await rabbit.publish_message(response_json,"02")
#                             logging.info("Response published to RabbitMQ")

#                     except json.JSONDecodeError as e:
#                         logging.error(f"Failed to decode JSON message: {e}")
#                     except Exception as e:
#                         logging.error(f"Error processing OCPP message: {e}")

#             await queue.consume(on_message)
#             logging.info("Consumer started and waiting for messages...")
#             await asyncio.Future()