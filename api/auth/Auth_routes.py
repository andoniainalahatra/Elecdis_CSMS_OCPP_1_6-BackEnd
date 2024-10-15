from fastapi import BackgroundTasks
from api.auth.Auth_models import *
from api.auth.Auth_services import *
from fastapi import APIRouter, HTTPException, status
router = APIRouter()


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: LoginData):
    session = next(get_session())
    try:
        generated_token = login(form_data.username, form_data.password, session)
        # user= await  get_current_user(session, generated_token.token)
        user=None
        return generated_token
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/register", response_model=Token)
async def register_user(registered_user: UserRegister):
    if registered_user.password != registered_user.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Password and confirm password do not match")
    newUser = User(first_name=registered_user.first_name,
                   last_name=registered_user.last_name,
                   email=registered_user.email,
                   phone=registered_user.phone,
                   id_subscription=registered_user.id_subscription,
                   id_user_group=registered_user.id_user_group,
                   id_partner=registered_user.id_partner,
                   password=registered_user.password
                   )
    session = next(get_session())
    user = None
    try:
        user = register(newUser, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return login(user.email, registered_user.password, session)

@router.post("/forgot-password")
async def forgot_password(email: str, tasks: BackgroundTasks):
    session = next(get_session())
    try:
        tasks.add_task(forgot_password_method, email, session)
        return {"message": "Recovery code sent to email", "status": "success","status_code":200, "email": email}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reset_password")
def reset_password(reset_request : ResetPassword, session : Session =Depends(get_session)):
    try:
        # check code
        check_code_reset(email=reset_request.email, code=reset_request.code,session=session)
        # save new password
        change_password(reset_request,session)
        return {
            "message": "Password reset successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/check_password_reset_code")
def check_password_reset_code(code:str,email:str, session : Session =Depends(get_session)):
    try:
        check_code_reset(email, code, session)
        return {
            "message": "Code is valid"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))