from datetime import timedelta
import re
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from api.exeptions.EmailException import EmailException
from api.exeptions.SubscriptionException import SubscriptionException
from api.users.UserServices import get_user_data, UserUpdate
from core.database import get_session
from models.elecdis_model import *
from sqlmodel import select

SECRET_KEY = "d343fdce6f2ca054a42914a06a0e519e842e2f6412d723acd016fd43715b1a59"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
PASSWORD_LENGTH = 6

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")





def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(session: Session, email: str):
    return session.exec(select(User).where(User.email == email)).first()


def check_email_if_exists(email: str, session: Session):
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        return False
    return True


def authenticate_user(session: Session, email: str, password: str):
    user = get_user(session, email)
    if not user:
        print("no user found")
        return False
    if not verify_password(password, user.password):
        print(verify_password(password, user.password))
        print("wrong password")
        return False
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(session : Session = Depends(get_session),token: str = Depends(oauth_2_scheme)):
    credetionals_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                           detail="Could not validate credentials",
                                           headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credetionals_exception
    except JWTError:
        raise credetionals_exception
    user = get_user(session, email)
    if user is None:
        raise credetionals_exception
    return get_user_data(user)


def verify_email_structure(email: str):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        raise EmailException(f"Email {email} is not valid")


def verify_password_length(password: str):
    if len(password) < PASSWORD_LENGTH:
        raise Exception("Password must be at least 8 characters")

def trim_data(user):
    user.first_name = user.first_name.strip()
    user.last_name = user.last_name.strip()
    user.email = user.email.strip()
    user.phone = user.phone.strip()
    user.password= user.password.strip()
    return user
def check_empty_fields(user: User):
    fields_to_check = ['first_name', 'last_name', 'email', 'phone', 'password']
    for field in fields_to_check:
        value = getattr(user, field, None)
        if value is None or value.strip() == "":
            raise ValueError(f"The field '{field}' cannot be empty.")
    return user


def validate_user(user, session : Session, check_email):
    verify_email_structure(user.email)
    verify_password_length(user.password)
    if check_email==True :
        if check_email_if_exists(user.email, session):
            raise EmailException(f"Email {user.email} already exists")
    # check subscription
    subscription = session.exec(select(Subscription).where(Subscription.id == user.id_subscription)).first()
    if subscription is None:
        raise SubscriptionException(f"Subscription {user.id_subscription} does not exist")
    # check userGroup
    userGroup = session.exec(select(UserGroup).where(UserGroup.id == user.id_user_group)).first()
    # check partner
    if user.id_partner is not None:
        partner = session.exec(select(Partner).where(Partner.id == user.id_partner)).first()
        if partner is None:
            raise Exception(f"Partner {user.id_partner} does not exist")
    if userGroup is None:
        raise Exception(f"UserGroup {user.id_userModel} does not exist")
def register(newUser: User, session: Session):
    validate_user(newUser, session,True)
    newUser = trim_data(newUser)
    check_empty_fields(newUser)
    newUser.password = get_password_hash(newUser.password)
    session.add(newUser)
    session.commit()
    session.refresh(newUser)
    return newUser
def login (username : str, password:str, session:Session):
    user = authenticate_user(session, username, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    user_data = get_user_data(user)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

def update_user(user_to_update:UserUpdate,  session: Session):
    validate_user(user_to_update,session, check_email=False)
    user_to_update = trim_data(user_to_update)
    check_empty_fields(user_to_update)
    user: User = session.exec(select(User).where(User.id == user_to_update.id)).first()
    user.first_name = user_to_update.first_name
    user.last_name = user_to_update.last_name
    user.email = user_to_update.email
    user.phone = user_to_update.phone
    user.id_user_group = user_to_update.id_user_group
    user.id_subscription = user_to_update.id_subscription
    user.id_partner = user_to_update.id_partner
    user.password= get_password_hash(user_to_update.password)
    session.add(user)
    session.commit()
    return user