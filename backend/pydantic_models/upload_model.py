from pydantic import BaseModel

# a quick tip :- we use BaseModel for the pydantic models and Base for the DB itself
class UploadMetadata(BaseModel):
    title: str
    description: str
    video_id: str
    video_s3_key: str
    visibility: str