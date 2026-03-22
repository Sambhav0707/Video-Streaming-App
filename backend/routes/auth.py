from db.middleware.auth_middleware import get_current_user
from fastapi import Cookie
from pydantic_models.auth_model import ConfirmUserRequest
from pydantic_models.auth_model import LoginRequest
from fastapi import HTTPException, Response
from db.models.users import User
from fastapi import APIRouter, Depends
import boto3
from pydantic_models.auth_model import SignUpRequest
from secret_keys import Settings
from helpers import auth_helper
from sqlalchemy.orm import Session
from db import db

router = APIRouter()  # a normal fastapi convention so that we keep the code separate

"""
initialising the cognito client using boto3
it is similar to firebase or supabase thing
we are contacting AWS with the user credentials
and telling it that here they are and now signup / login
"""

# initialising the settings
settings = Settings()

REGION_NAME = settings.REGION_NAME
cognito_client = boto3.client(
    "cognito-idp", region_name=REGION_NAME
)  # cognito-idp :- A low-level client representing Amazon Cognito Identity Provider
# NOTE:- in boto3.client() you also have to give access key and region etc but we are not beCAUSE WE HAVE DONE AWS CONFIGURE ALREADY

"""
defining the constants of the AWS Cognito 
"""
COGNITO_CLIENT_KEY = settings.COGNITO_CLIENT_KEY
COGNITO_SECRET_CLIENT_KEY = settings.COGNITO_SECRET_CLIENT_KEY

"""
SIGNUP ROUTE
"""


@router.post("/signup")
def sign_up_user(request_data: SignUpRequest, DB: Session = Depends(db.get_db)):
    try:
        # calculating the secret hash
        secret_hash = auth_helper.get_secret_hash(
            username=request_data.email,
            client_id=COGNITO_CLIENT_KEY,
            secret_hash=COGNITO_SECRET_CLIENT_KEY,
        )
        # calling the cognito client to sign up the user
        sign_up_response = cognito_client.sign_up(
            ClientId=COGNITO_CLIENT_KEY,
            # SecretHash is a hash of the client ID and the username,
            # why we are passing that ?
            # -> because any body can have the username and password even the client_id is
            # public so we need a source of truth in this
            SecretHash=secret_hash,
            Username=request_data.email,
            Password=request_data.password,
            UserAttributes=[
                {
                    "Name": "email",
                    "Value": request_data.email,
                },
                {
                    "Name": "name",
                    "Value": request_data.name,
                },
            ],
        )

        # now after the user is created in the cognito we fetch the user_sub from the response bcz
        # we have a coloumn named cognito_sub in our users table
        cognito_sub = sign_up_response["UserSub"]

        # checking if the cognito sub is not present then raising an exception
        if not cognito_sub:
            raise HTTPException(
                status_code=400, detail="Cognito did not return a valid user sub"
            )

        # now we create a user for our DATABASE
        new_user = User(
            name=request_data.name, email=request_data.email, cognito_sub=cognito_sub
        )

        # adding the new user to the database
        DB.add(new_user)
        DB.commit()
        """
        we are doing DB.refresh(new_user) so that we can get the id of the new user
        but we are returning the message only but it is a good practice to refresh the user
        """
        DB.refresh(new_user)

        return {"message": "User created successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cognito SignUp Exception : {e}")


"""
SIGNIN ROUTE
"""


@router.post("/login")
def login_user(request_data: LoginRequest, response: Response):
    try:
        # calculating the secret hash
        secret_hash = auth_helper.get_secret_hash(
            username=request_data.email,
            client_id=COGNITO_CLIENT_KEY,
            secret_hash=COGNITO_SECRET_CLIENT_KEY,
        )
        # calling the cognito client to signin the user
        sign_in_response = cognito_client.initiate_auth(
            ClientId=COGNITO_CLIENT_KEY,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": request_data.email,
                "PASSWORD": request_data.password,
                "SECRET_HASH": secret_hash,
            },
        )

        """
        To keep the persistence auth we are using the cookies method in which we are 
        storing the access token and the refresh token in the cookies
        """
        # getting the login response from the cognito
        auth_result = sign_in_response["AuthenticationResult"]

        if not auth_result:
            raise HTTPException(
                status_code=400, detail="Cognito did not return a valid auth result"
            )

        # gettin the access token and the refresh token from the auth result
        access_token = auth_result["AccessToken"]
        refresh_token = auth_result["RefreshToken"]

        # setting the cookies
        response.set_cookie(
            key="access_token", value=access_token, httponly=True, secure=True
        )
        response.set_cookie(
            key="refresh_token", value=refresh_token, httponly=True, secure=True
        )

        return sign_in_response

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cognito SignUp Exception : {e}")


"""
CONFIRM USER ROUTE
"""


@router.post("/confirm-user")
def confirm_user(request_data: ConfirmUserRequest):
    try:
        # calculating the secret hash
        secret_hash = auth_helper.get_secret_hash(
            username=request_data.email,
            client_id=COGNITO_CLIENT_KEY,
            secret_hash=COGNITO_SECRET_CLIENT_KEY,
        )
        # calling the cognito client to confirm the user
        confirm_user_response = cognito_client.confirm_sign_up(
            ClientId=COGNITO_CLIENT_KEY,
            Username=request_data.email,
            SecretHash=secret_hash,
            ConfirmationCode=request_data.otp,
        )

        return {"message": "User confirmed successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cognito SignUp Exception : {e}")


"""
REFRESH TOKEN ROUTE
"""


@router.post("/refresh-token")
def refresh_token(
    refresh_token: str = Cookie(None),
    response: Response = None,
    user_cognito_sub: str = Cookie(None),
):
    try:
        if not refresh_token or not user_cognito_sub:
            raise HTTPException(400, "cookies cannot be null!")
        # calculating the secret hash
        secret_hash = auth_helper.get_secret_hash(
            username=user_cognito_sub,  # we are using the user_cognito_sub as the username because we will have to store the cognito_sub in the client side cookies
            client_id=COGNITO_CLIENT_KEY,
            secret_hash=COGNITO_SECRET_CLIENT_KEY,
        )
        # calling the cognito client to refresh the token
        refresh_token_response = cognito_client.initiate_auth(
            ClientId=COGNITO_CLIENT_KEY,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={
                "REFRESH_TOKEN": refresh_token,
                "SECRET_HASH": secret_hash,
            },
        )

        # setting up the new cookies
        auth_result = refresh_token_response["AuthenticationResult"]
        if not auth_result:
            raise HTTPException(
                status_code=400, detail="Cognito did not return a valid auth result"
            )

        # gettin the access token and the refresh token from the auth result
        access_token = auth_result["AccessToken"]

        # setting the cookies
        response.set_cookie(
            key="access_token", value=access_token, httponly=True, secure=True
        )

        return {"message": "Token refreshed successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cognito SignUp Exception : {e}")


"""
A ROUTE FOR GETTING THE USER DETAILS THROUGH THE MIDDLEWARE
"""

"""
so we add user_data = Depends(get_current_user) to ensure only authenticated users only can 
access the route :- /auth/me
"""


@router.get("/me")
def get_user_data_through_protected_route(user_data=Depends(get_current_user)):
    return {"message": "User Successfully Authorised.", "user": user_data}
