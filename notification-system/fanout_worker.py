"""
Fan-out Worker
==============
Subscribes to `video-uploaded`.

For each event:
  1. Reads the creator's followers in pages from FollowerStore
  2. For each page, publishes ONE Pub/Sub message to `notification-batch`
     containing a batch of user IDs

This means a creator with 10M followers generates:
  10_000_000 / 500 = 20,000  batch messages

Each batch message is processed independently by a Notification Worker.
This is the core horizontal scaling primitive.

Production: Run as a Cloud Run Job or GKE Deployment with multiple replicas.
Pub/Sub guarantees each message is delivered to exactly one fanout worker
replica (competing consumers).
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor
from google.cloud import pubsub_v1
import config
from follower_store import FollowerStore
from models import NotificationBatch


class FanoutWorker:
    def __init__(self, follower_store: FollowerStore):
        self.follower_store = follower_store
        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher  = pubsub_v1.PublisherClient()

        self.sub_path   = self.subscriber.subscription_path(
            config.PROJECT_ID, config.FANOUT_SUBSCRIPTION
        )
        self.batch_topic = self.publisher.topic_path(
            config.PROJECT_ID, config.NOTIFICATION_BATCH_TOPIC
        )

    def _publish_batch(self, batch: NotificationBatch):
        data = json.dumps(batch.to_dict()).encode("utf-8")
        self.publisher.publish(
            self.batch_topic,
            data,
            batch_id=batch.batch_id,
            creator_id=batch.creator_id,
        )

    def _handle_message(self, message):
        try:
            event = json.loads(message.data.decode("utf-8"))
            creator_id = event["creator_id"]
            video_id   = event["video_id"]
            title      = event["title"]

            follower_count = self.follower_store.count(creator_id)
            print(f"[FanoutWorker] creator={creator_id} followers={follower_count:,} "
                  f"→ fanning out for video='{title}'")

            batches_published = 0
            futures = []

            for user_ids in self.follower_store.iter_followers(creator_id, config.FOLLOWER_BATCH_SIZE):
                batch = NotificationBatch.create(creator_id, video_id, title, user_ids)
                data = json.dumps(batch.to_dict()).encode("utf-8")
                future = self.publisher.publish(
                    self.batch_topic, data,
                    batch_id=batch.batch_id,
                    creator_id=creator_id,
                )
                futures.append(future)
                batches_published += 1

            # Wait for all publishes to confirm
            for f in futures:
                f.result()

            print(f"[FanoutWorker] Done — published {batches_published} batches "
                  f"({batches_published * config.FOLLOWER_BATCH_SIZE:,} notifications enqueued)")
            message.ack()

        except Exception as e:
            print(f"[FanoutWorker] ERROR: {e}")
            message.nack()   # Pub/Sub will redeliver with backoff

    def run(self):
        print(f"[FanoutWorker] Listening on {self.sub_path} ...")
        flow_control = pubsub_v1.types.FlowControl(max_messages=10)
        streaming_pull = self.subscriber.subscribe(
            self.sub_path,
            callback=self._handle_message,
            flow_control=flow_control,
        )
        try:
            streaming_pull.result()
        except KeyboardInterrupt:
            streaming_pull.cancel()
            streaming_pull.result()
