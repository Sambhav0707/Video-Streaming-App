from pydantic_models.upload_model import UploadMetadata
import boto3
from fastapi import HTTPException
from db.middleware.auth_middleware import get_current_user
from fastapi import Depends
from fastapi import APIRouter
from secret_keys import Settings
import uuid
from db import db
from sqlalchemy.orm import Session
from db.models.videos import Video

# defining the router
api_router = APIRouter()

# settings (used for getting env variables)
settings = Settings()

# boto3 client
s3_client = boto3.client("s3", region_name=settings.REGION_NAME)

"""
this is going to be prefixed as :- /video/upload/url

this is for getting the presigned url
"""


@api_router.get("/url")
def get_presigned_url(user=Depends(get_current_user)):
    try:
        # Constructing the unique S3 object key (destination path):
        # 1. 'videos/...': Base directory for uploads.
        # 2. 'user["sub"]': Isolates videos by the uploader's unique ID to organize files and avoid cross-user collisions.
        # 3. 'uuid.uuid4()': Ensures every uploaded file has a unique name, preventing accidental overwrites.
        video_id = f"videos/{user['sub']}/{uuid.uuid4()}.mp4"
        # getting the presigned url
        response = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.AWS_RAW_VIDEO_BUCKET,
                # this key becomes very important here because
                # this key should be the same in the client side also
                "Key": video_id,
                "ContentType": "video/mp4",
            },
        )

        return {"url": response, "video_id": video_id}

    except Exception as e:
        raise HTTPException(500, str(e))


@api_router.get("/url/thumbnail")
def get_presigned_url_thumbnails(thumbnail_id: str, user=Depends(get_current_user)):
    try:
        # Constructing the unique S3 object key (destination path):
        # 1. 'videos/...': Base directory for uploads.
        # 2. 'user["sub"]': Isolates videos by the uploader's unique ID to organize files and avoid cross-user collisions.
        # 3. 'uuid.uuid4()': Ensures every uploaded file has a unique name, preventing accidental overwrites.
        thumbnail_id = thumbnail_id.replace("videos/", "thumbnails/").replace(
            ".mp4", ""
          )
        # getting the presigned url
        response = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.AWS_RAW_VIDEO_THUMBNAIL_BUCKET,
                # this key becomes very important here because
                # this key should be the same in the client side also
                "Key": thumbnail_id,
                "ContentType": "image/jpg",
                "ACL": "public-read",
            },
        )

        return {"url": response, "thumbnail_id": thumbnail_id}

    except Exception as e:
        raise HTTPException(500, str(e))


"""
Route for uploading the metadata to the postgres instance
"""


@api_router.post("/metadata")
def upload_metadata(
    metadata: UploadMetadata,  # pydantic model representing what to sent to the DB
    user=Depends(get_current_user),
    db: Session = Depends(db.get_db),  # this route requires some db operations
):
    # creating a new video object
    new_video = Video(
        id=metadata.video_id,
        title=metadata.title,
        description=metadata.description,
        video_s3_key=metadata.video_s3_key,
        visibility=metadata.visibility,
        user_id=user["sub"],
    )

    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    return new_video
