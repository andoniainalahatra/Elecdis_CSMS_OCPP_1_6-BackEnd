from pydantic import BaseModel
from typing import Optional
from api.users.UserServices import UserData


class Token(BaseModel):
    access_token: str
    token_type: str
    user:UserData


class UserRegister(BaseModel):
    first_name: str
    last_name: str
    password: str
    confirm_password: str
    email: str
    phone:str
    id_subscription: int
    id_user_group: int
    id_partner: Optional[int] = None

class LoginData(BaseModel):
    username:str
    password:str

class ResetPassword(BaseModel):
    email:str
    code:str
    new_password:str
    confirm_password:str
