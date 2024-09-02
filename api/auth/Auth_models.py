from pydantic import BaseModel
class Token(BaseModel):
    access_token: str
    token_type: str


class UserRegister(BaseModel):
    first_name: str
    last_name: str
    password: str
    confirm_password: str
    email: str
    phone:str
    id_subscription: int
    id_user_group: int
    id_partner: int | None = None

class LoginData(BaseModel):
    username:str
    password:str