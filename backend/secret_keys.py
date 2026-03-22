from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

"""
we are using .env for storing the keys and secrets keys 
now to access them we can easily use pydantic_settings feature 

-> by importing BaseSettings and defining the class Settings that inherits from BaseSettings
-> we mentioned the exact key names that are used in the .env file
-> and that is how it binds the keys name and let us access them 

NOTE : we are not mentioning the exact location of .env file because the .env and this file is at the same level in the 
folder :- backend
"""


class Settings(BaseSettings):
    COGNITO_CLIENT_KEY: str = ""
    COGNITO_SECRET_CLIENT_KEY: str = ""
    REGION_NAME: str = ""
    POSTGRES_URL: str = ""
    AWS_RAW_VIDEO_BUCKET: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_RAW_VIDEO_THUMBNAIL_BUCKET: str = ""
