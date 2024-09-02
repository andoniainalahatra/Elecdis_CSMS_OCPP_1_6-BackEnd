from typing import Annotated
from fastapi import Depends, HTTPException, status

from api.auth.Auth_services import get_current_user
from models.elecdis_model import User


class RoleChecker :
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[User, Depends(get_current_user)]):
        if user.role in self.allowed_roles:
            return True
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to access this resource")
