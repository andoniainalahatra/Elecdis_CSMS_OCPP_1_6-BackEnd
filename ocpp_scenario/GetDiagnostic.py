import uuid
import datetime
class GetDiagnostic:
    def generate_message_id(self):
        return str(uuid.uuid4())
    def on_getdiagnostic(self,startTime:datetime,stopTime:datetime,path:str):
        message_id=self.generate_message_id()
        return [2,message_id,"GetDiagnostics",{
        "location": path,  
        "retries": 3,  
        "retryInterval": 60,  
        "startTime": startTime,  
        "stopTime":  stopTime  
        }
        ]
