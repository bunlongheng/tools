from dataclasses import dataclass, field
from typing import List
import time, uuid

@dataclass
class VideoUploadedEvent:
    creator_id: str
    video_id: str
    title: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self):
        return self.__dict__

@dataclass
class NotificationBatch:
    """One Pub/Sub message = one batch of user IDs to notify."""
    batch_id: str
    creator_id: str
    video_id: str
    title: str
    user_ids: List[str]
    timestamp: float = field(default_factory=time.time)

    @staticmethod
    def create(creator_id, video_id, title, user_ids):
        return NotificationBatch(
            batch_id=str(uuid.uuid4()),
            creator_id=creator_id,
            video_id=video_id,
            title=title,
            user_ids=user_ids,
        )

    def to_dict(self):
        return self.__dict__
