import os
import random
from datetime import timedelta
import re
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from api.auth.Auth_models import ResetPassword
from api.exeptions.EmailException import EmailException
from api.exeptions.SubscriptionException import SubscriptionException
from api.users.UserServices import *
from api.users.UserServices import get_user_from_email
from core.database import get_session
from models.elecdis_model import *
from sqlmodel import select, and_
from api.mail.email_model import Email_model, send_email
from ecdsa import (SigningKey, NIST256p ,VerifyingKey)
from cryptography.hazmat.primitives import serialization

PRIVATE_KEY = SigningKey.generate(curve=NIST256p)
PUBLIC_KEY = PRIVATE_KEY.get_verifying_key()

private_key_pem = PRIVATE_KEY.to_pem()
public_key_pem = PUBLIC_KEY.to_pem()

ALGORITHM = "ES256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
PASSWORD_LENGTH = 6

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def load_keys(private_key_path, public_key_path):
    with open(private_key_path, 'rb') as key_file:
        private_key_pem = key_file.read()
    private_key = SigningKey.from_pem(private_key_pem)

    with open(public_key_path, 'rb') as key_file:
        public_key_pem = key_file.read()
    public_key = VerifyingKey.from_pem(public_key_pem)

    return private_key, public_key
def generate_keys():
    # create a file to store the private key
    main_file_directory = os.path.dirname(os.path.abspath(__file__))
    filePath=f'{main_file_directory}/private'
    if not os.path.exists(f'{filePath}/private.pem') and not os.path.exists(f'{filePath}/public.pem'):
        os.makedirs(filePath, exist_ok=True)
        private_key_path=f"{filePath}/private.pem"
        public_key_path=f"{filePath}/public.pem"

        # Générer la clé privée
        private_key = SigningKey.generate(curve=NIST256p)
        private_key_pem = private_key.to_pem()
        # Enregistrer la clé privée dans un fichier
        with open(private_key_path, 'wb') as f:
            f.write(private_key_pem)

        # Générer la clé publique à partir de la clé privée
        public_key = private_key.get_verifying_key()
        public_key_pem = public_key.to_pem()
        # Enregistrer la clé publique dans un fichier
        with open(public_key_path, 'wb') as f:
            f.write(public_key_pem)


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def check_email_if_exists(email: str, session: Session):
    user = get_user_from_email(email=email, session=session)
    if user is None:
        return False
    return True


def authenticate_user(session: Session, email: str, password: str):
    user = get_user_from_email(email=email, session=session)
    user_group = session.exec(select(UserGroup).where(UserGroup.id == user.id_user_group)).first()
    if(user_group.name != ADMIN_NAME):
        return False
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
    encoded_jwt = jwt.encode(
        to_encode,
        private_key_pem,
        algorithm=ALGORITHM
    )
    return encoded_jwt


async def get_current_user(session: Session = Depends(get_session), token: str = Depends(oauth_2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Use the public key to verify the JWT
        payload = jwt.decode(token, public_key_pem, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_from_email(email=email, session=session)
    if user is None:
        raise credentials_exception
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
    user.password = user.password.strip()
    return user


def check_empty_fields(user: User):
    fields_to_check = ['first_name', 'last_name', 'email', 'phone', 'password']
    for field in fields_to_check:
        value = getattr(user, field, None)
        if value is None or value.strip() == "":
            raise ValueError(f"The field '{field}' cannot be empty.")
    return user


def validate_user(user, session: Session, check_email):
    verify_email_structure(user.email)
    verify_password_length(user.password)
    if check_email == True:
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
    validate_user(newUser, session, True)
    newUser = trim_data(newUser)
    check_empty_fields(newUser)
    newUser.password = get_password_hash(newUser.password)
    session.add(newUser)
    session.commit()
    session.refresh(newUser)
    return newUser


def login(username: str, password: str, session: Session):
    user = authenticate_user(session, username, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    user_data = get_user_data(user)
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token, "token_type": "bearer","user":user_data}


def update_user(user_to_update:UserUpdate, session: Session, user_id: int):
    user: User = get_user_by_id(user_id, session)
    if user is None:
        raise Exception(f"User with id {user_id} does not exist")
    if user_to_update.first_name is not None:
        user.first_name = user_to_update.first_name.strip()
    if user_to_update.last_name is not None:
        user.last_name = user_to_update.last_name.strip()
    if user_to_update.email is not None:
        try:
            verify_email_structure(user_to_update.email)
            if check_email_if_exists(user.email, session) and user.email != user_to_update.email:
                raise EmailException(f"Email {user.email} already exists")
            user.email = user_to_update.email
        except EmailException as e:
            raise e
    if user_to_update.phone is not None:
        user.phone = user_to_update.phone.strip()
    if user_to_update.id_user_group is not None:
        userGroup = session.exec(select(UserGroup).where(UserGroup.id == user.id_user_group)).first()
        if userGroup is None:
            raise Exception(f"UserGroup {user.id_userModel} does not exist")
        user.id_user_group = user_to_update.id_user_group
    if user_to_update.id_subscription is not None:
        subscription = session.exec(select(Subscription).where(Subscription.id == user.id_subscription)).first()
        if subscription is None:
            raise SubscriptionException(f"Subscription {user.id_subscription} does not exist")
        user.id_subscription = user_to_update.id_subscription
    if user_to_update.id_partner is not None:
        partner = session.exec(select(Partner).where(Partner.id == user.id_partner)).first()
        if partner is None:
            raise Exception(f"Partner {user.id_partner} does not exist")
        user.id_partner = user_to_update.id_partner
    if user_to_update.password is not None:
        user.password = get_password_hash(user_to_update.password)



    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    return user


def generate_recovery_code(length=6):
    recovery_code = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return recovery_code


async def forgot_password_method(email: str, session: Session):
    user = get_user_from_email(email=email, session=session)
    if user is None:
        raise EmailException(f"User with email {email} does not exist")
    recovery_code = generate_recovery_code()
    expiration_date = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # save recovery code in the database
    user_code: User_reset_code = User_reset_code(user_id=user.id, code=recovery_code, expiration_date=expiration_date,
                                                 is_used=False)
    session.add(user_code)
    session.commit()
    # -
    # send email with recovery code
    email_moddel = Email_model(username=user.first_name, code=recovery_code, email=email)
    await send_email(email_moddel, recipient=[email])
    return "recovery code sent successfully"


def check_code_reset(email: str, code: str, session: Session = Depends(get_session)):
    user = get_user_from_email(email=email, session=session)
    if user is None:
        raise EmailException(f"User with email {email} does not exist")
    user_code = session.exec(
        select(User_reset_code).
        where(and_(
            User_reset_code.user_id == user.id,
            User_reset_code.code == code))).first()
    if user_code is None:
        raise Exception(f"Code {code} does not exist")
    if user_code.is_used:
        raise Exception(f"Code {code} has already been used")
    if user_code.code != code:
        raise Exception(f"Code {code} is incorrect")
    if user_code.expiration_date < datetime.utcnow():
        raise Exception(f"Code {code} has expired")
    return user


def change_password(reset_password: ResetPassword, session: Session = Depends(get_session)):
    try:
            code_reset = session.exec(
                select(User_reset_code).where(User_reset_code.code == reset_password.code)).first()
            code_reset.is_used = True
            session.add(code_reset)
            user: User = get_user_from_email(email=reset_password.email, session=session)
            if reset_password.new_password != reset_password.confirm_password:
                raise Exception("Password and confirm password do not match")
            user.password = get_password_hash(reset_password.new_password)
            session.add(user)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    return "Password reset successfully"
