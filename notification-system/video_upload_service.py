"""
Video Upload Service
====================
When a creator uploads a video, this service publishes ONE event
to the `video-uploaded` Pub/Sub topic.

Production equivalent: a Cloud Run service behind an API gateway.
"""

import json
from google.cloud import pubsub_v1
import config
from models import VideoUploadedEvent


class VideoUploadService:
    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(
            config.PROJECT_ID, config.VIDEO_UPLOADED_TOPIC
        )

    def upload(self, creator_id: str, video_id: str, title: str):
        event = VideoUploadedEvent(
            creator_id=creator_id,
            video_id=video_id,
            title=title,
        )
        data = json.dumps(event.to_dict()).encode("utf-8")

        future = self.publisher.publish(
            self.topic_path,
            data,
            creator_id=creator_id,   # Pub/Sub message attributes for filtering
            video_id=video_id,
        )
        msg_id = future.result()
        print(f"[VideoUploadService] Published event → msg_id={msg_id} "
              f"creator={creator_id} video={video_id} title='{title}'")
        return msg_id
