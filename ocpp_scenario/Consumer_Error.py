import asyncio
import logging
import aio_pika
import websockets
import json
from aio_pika import IncomingMessage
from api.Historique_defaillance.Historique_defaillance_models import Historique_defaillance_create,Historique_defaillance_update
from api.Historique_defaillance.Historique_defaillance_services import update_historique_defaillance,create_historique_defaillance
from websockets.exceptions import WebSocketException
from core.database import get_session
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from core.config import TIME_ZONE
import pytz
import time


class ConsumerError:
    last_error = {} 
    @staticmethod
    def format_error_message(ocpp_error_message,charge_point_id):
        """
        Cette méthode formate le message d'erreur OCPP en un format lisible pour l'utilisateur.
        """
        # Décomposer le message OCPP brut
        message_type, message_id, error_code, error_description, details = ocpp_error_message

        # Dictionnaire de correspondance des erreurs
        error_mapping = {
            "NotSupported": "L'action demandée est reconnue mais n'est pas prise en charge par le serveur.",
            "InternalError": "Une erreur interne est survenue. Le serveur n'a pas pu traiter la demande.",
            "ProtocolError": "Le message envoyé est incomplet ou incorrect. Veuillez vérifier les informations.",
            "SecurityError": "Un problème de sécurité a empêché le serveur de traiter la demande.",
            "FormationViolation": "Le message est incorrect et ne respecte pas la structure attendue.",
            "PropertyConstraintViolation": "Une des valeurs fournies est invalide. Vérifiez les informations saisies.",
            "OccurenceConstraintViolation": "Un des champs du message viole les contraintes de fréquence ou d'occurrence.",
            "TypeConstraintViolation": "Une des valeurs du message n'est pas du type attendu.",
            "GenericError": "Une erreur inconnue est survenue. Veuillez réessayer plus tard."
        }

        # Créer un message lisible pour l'utilisateur final
        formatted_message = {
            "type": "Erreur de traitement",
            "message_id": message_id,
            "erreur": error_code,
            "description": error_mapping.get(error_code, "Une erreur est survenue."),
            "details": details if details else "Pas de détails supplémentaires."
        }
        return formatted_message
    @staticmethod
    def should_store_error(charge_point_id, error_code):
        """
        Vérifie si l'erreur doit être stockée et si une notification doit être envoyée.
        """
        current_time = time.time()
        error_key = f"{charge_point_id}_{error_code}"
        
        # Vérifier si l'erreur existe déjà
        if error_key in ConsumerError.last_error:
            last_time = ConsumerError.last_error[error_key]
            # Si la même erreur s'est produite il y a moins de 2 heures, on ne la stocke pas
            if current_time - last_time < 3 * 60 * 60:  # 2 heures en secondes
                return False

        # Mettre à jour l'heure de la dernière erreur
        ConsumerError.last_error[error_key] = current_time
        return True  
    async def consume_messages(connection):
        from ocpp_scenario.Connexion_web import Connexion
        session=next(get_session())
        async with connection:
            channel = await connection.channel()        
            queue = await channel.get_queue("notification_error")
            async def on_message(message: IncomingMessage):
                async with message.process():
                    raw_message = message.body.decode()
                   
                    try:
                        ocpp_message = json.loads(raw_message)
                        if isinstance(ocpp_message, dict):
                            payload = ocpp_message.get("payload")
                            charge_point_id = ocpp_message.get("charge_point_id")
                            formatted_error = ConsumerError.format_error_message(payload,charge_point_id)
                            if ConsumerError.should_store_error(charge_point_id, formatted_error.get("erreur")):
                                connexion = Connexion()
                                timezone = pytz.timezone(TIME_ZONE)
                                historique = Historique_defaillance_create(
                                    charge_point_id=charge_point_id,
                                    time=datetime.now(timezone),
                                    Error_code=formatted_error.get("erreur"),
                                    Description=formatted_error.get("description")
                                )
                                create_historique_defaillance(histo=historique, session=session)
                                
                                await connexion.notify_frontend_of_error(
                                    f"{formatted_error.get('erreur')}: {formatted_error.get('description')}  pour charge point = {charge_point_id}"
                                )
                           
                        
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
            
