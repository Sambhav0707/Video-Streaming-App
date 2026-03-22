from fastapi import Cookie
import boto3
from fastapi import HTTPException
from secret_keys import Settings

"""
A centralised middleware for authentication 
"""
settings = Settings()
cognito_client = boto3.client("cognito-idp", region_name=settings.REGION_NAME)

"""
_get_user_from_cognito() :- A private function to get the current user from the cognito database

the reason why we are making it Private is that we dont want it to get accessed outside of this. 
"""


def _get_user_from_cognito(access_token: str):
    try:
        # getting the user data from the cognito
        user_response_data = cognito_client.get_user(AccessToken=access_token)
        """
        returning the response so that we only get UserAttributes value only

        so the response containes :- 
        [
            {
                "Name" : "Sambhav",
                "Value" : "07"
            }
        ]

        we are turning that into :- 
        {
            "Sambhav" : "07"
        }
        """
        user_data = {
            attr["Name"]: attr["Value"]
            for attr in user_response_data.get("UserAttributes", [])
        }
        return user_data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to get user from cognito : {e}"
        )


"""
NOTE:- In real world Application we should have called out database (POSTGRESQL) for the user data because 
that would have contained the user_id that could have helped us to connect other tables also!!

But in our case we are simply calling cognito for getting the user data (Not a recommended approach)
"""


def get_current_user(access_token: str = Cookie(None)):
    try:
        # if access_token was None we throw exception that user is not authorised
        if not access_token:
            raise HTTPException(status_code=401, detail=f"User Not authorised")

        return _get_user_from_cognito(access_token=access_token)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong while getting the current user: {e}",
        )
