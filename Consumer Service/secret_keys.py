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
folder :- Consumer Service
"""


class Settings(BaseSettings):
    REGION_NAME: str = ""
    AWS_SQS_VIDEO_PROCESSING_QUEUE_URL: str = ""
    ECS_CLUSTER_ARN: str = ""
    ECS_TASK_DEFINETION:str =""
