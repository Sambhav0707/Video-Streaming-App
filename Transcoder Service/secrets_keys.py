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
folder :- Transcoder Service
"""

'''
WE ARE taking the S3_BUCKET_NAME AND S3_KEY from the CONSUMER SERVICE but the reason why we are putting them 
here as system variables because we have to containerise this so container is itself a mini system.
'''
class Settings(BaseSettings):
    REGION_NAME: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = ""
    S3_KEY: str = ""
    S3_PROCESSED_VIDEOS_BUCKET: str=""
    BACKEND_URL:str =""


    
    