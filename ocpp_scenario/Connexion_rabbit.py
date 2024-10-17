import aio_pika
import json
from fastapi import FastAPI
from pydantic import BaseModel
import logging
from aio_pika import ExchangeType, Message as AioPikaMessage,IncomingMessage
import asyncio
from core.config import *


class Connexion_rabbit:
    def __init__(self):
        self.connection: aio_pika.Connection = None
        self.channel: aio_pika.Channel = None

    async def get_rabbit_connection(self):    
        try:
            self.connection = await aio_pika.connect_robust(CONNECTION_RABBIT)
            #logging.info("Connection to RabbitMQ established")
            return self.connection
        except Exception as e:
            logging.error(f"Error connecting to RabbitMQ: {e}")
            raise


    async def config_rabbit(self):
        
        self.connection = await self.get_rabbit_connection()
        async with self.connection:  # Connexion en mode contextuel
            channel = await self.connection.channel()  # Crée un canal
            exchange = await channel.declare_exchange("micro_ocpp", ExchangeType.DIRECT)
            queue1 = await channel.declare_queue("queue_1")
            queue2=await channel.declare_queue("queue_2")
            queue3=await channel.declare_queue("connection_close")
            queue4=await channel.declare_queue("notification_error")
            # Lier les queues à l'échange avec des clés de routage
            await queue1.bind(exchange,routing_key="01")
            await queue2.bind(exchange,routing_key="02")
            await queue3.bind(exchange,routing_key="03")
            await queue4.bind(exchange,routing_key="04")

    async def publish_message(self,content:list,routing:str):
        try:
            message_str = json.dumps(content)
            self.connection = await self.get_rabbit_connection()
            async with self.connection:
                channel = await self.connection.channel()
                exchange = await channel.get_exchange("micro_ocpp")  # Assurez-vous que l'échange est nommé correctement
                await exchange.publish(
                    AioPikaMessage(body=message_str.encode()),
                    routing_key=routing
                    
                )
            return {"status": "Message published"}
        except Exception as e:
            logging.error(f"Error publishing message: {e}")
            raise
        
        


