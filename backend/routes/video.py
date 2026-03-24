import json
from sqlalchemy.orm import Session
from db.models.videos import Video, ProcessingStatus, VisibilityStatus
from db.middleware.auth_middleware import get_current_user
from db.db import get_db
from fastapi import Depends, HTTPException
from fastapi import APIRouter
from sqlalchemy import (
    or_,
)  # or_ is used for performing conditional queries like if a == b or a == c
from db.redis_db import redis_client


api_router = APIRouter()

"""
Route for getting all the videos 
it is a simple one here we are just filtering the db on the bases of 
videos who are completed and public
"""


@api_router.get("/all")
def get_all_videos(db: Session = Depends(get_db), user=Depends(get_current_user)):
    videos = (
        db.query(Video)
        .filter(
            Video.is_processing == ProcessingStatus.COMPLETED,
            Video.visibility == VisibilityStatus.PUBLIC,
        )
        .all()
    )
    print(videos)
    return videos


"""
Route for getting one video
here we will use redis as a cache aside pattern 

NOTE: this route is not being used in the client side because we are using flutter theere routing works 
differently then the web frameworks like react

How it works (Cache-Aside):
-> Check Redis for video:{video_id}.
-> Cache Hit: Return the cached metadata.
-> Cache Miss: Query the database. If found, serialize the video object, store it in Redis with a longer TTL (like 1 hour or 24 hours, since individual video metadata rarely changes), and return it.

Cache Invalidation: If the video owner updates the video title/description, or changes visibility from PUBLIC to PRIVATE, 
we must delete or update the video:{video_id} key in Redis.
"""


@api_router.get("/{video_id}")
def get_video(
    video_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    # first we check for the key if it is present in the redis or not
    cache_key = f"video:{video_id}"
    cache_data = redis_client.get(cache_key)
    print(f"this is cache {cache_data}")
    if cache_data:
        # the reason we are doing json.loads()
        # is because we are storing the data in redis using json.dumps so it
        # convertes the data into a string/bytes
        return json.loads(cache_data)
    video = (
        db.query(Video)
        .filter(
            Video.id == video_id,
            Video.is_processing == ProcessingStatus.COMPLETED,
            # this mean the videos those who are public or their link to them is available
            or_(
                Video.visibility == VisibilityStatus.PUBLIC,
                Video.visibility == VisibilityStatus.UNLISTED,
            ),
        )
        .first()
    )
    if video:
        redis_client.setex(cache_key, 3600, json.dumps(video.to_dict()))

    return video


@api_router.put("/")
def update_video_by_id(id: str, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == id).first()

    if not video:
        raise HTTPException(404, "Video not found!")

    video.is_processing = ProcessingStatus.COMPLETED
    db.commit()
    db.refresh(video)

    return video
