from pydantic._internal._known_annotated_metadata import TEXT_SCHEMA_TYPES
from db.base import Base
from sqlalchemy import Column, TEXT, Integer, ForeignKey, Enum
import enum

"""
THis is just a addon but it is not nesecessary for this app incase in the 
future if we expand its functionality it will be a usefull addon.
"""


class VisibilityStatus(enum.Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"
    UNLISTED = "UNLISTED"  # this means like in yt when we upload a video and it is only show when we open its url


class ProcessingStatus(enum.Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"


class Video(Base):
    __tablename__ = "videos"

    id = Column(TEXT, primary_key=True)
    title = Column(TEXT)
    description = Column(TEXT)
    user_id = Column(TEXT, ForeignKey("users.cognito_sub"))
    # here we can see an observation while uploading the video to s3
    # we get presigned url so in that we also get s3_key
    # so while uploading the metadata to postgeres we already have the s3 key
    video_s3_key = Column(TEXT)
    visibility = Column(
        Enum(VisibilityStatus),
        nullable=False,
        default=VisibilityStatus.PRIVATE,
    )
    is_processing = Column(
        Enum(ProcessingStatus),
        nullable=False,
        default=ProcessingStatus.IN_PROGRESS,
    )

    """
    This function converts the model to a dict
    """
    def to_dict(self):
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if isinstance(value, enum.Enum):
                value = value.value
            result[c.name] = value
        return result
