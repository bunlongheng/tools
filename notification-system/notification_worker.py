"""
Notification Worker
===================
Subscribes to `notification-batch`.

For each batch message:
  1. Extracts list of user IDs
  2. (Optional) filters users who disabled notifications — Redis lookup
  3. Dispatches push / in-app / email notifications in parallel

Multiple replicas run simultaneously — Pub/Sub load-balances across them.

Production dispatch options:
  - Firebase Cloud Messaging (FCM) for mobile push
  - APNs for iOS
  - SendGrid / SES for email
  - Write to DynamoDB/Cassandra for in-app inbox
"""

import json
import time
import uuid
from google.cloud import pubsub_v1
import config
from notification_store import NotificationStore, Notification


class NotificationWorker:
    def __init__(self, store: NotificationStore, worker_id: str = "worker-1"):
        self.store       = store
        self.worker_id   = worker_id
        self.subscriber  = pubsub_v1.SubscriberClient()
        self.sub_path    = self.subscriber.subscription_path(
            config.PROJECT_ID, config.NOTIFICATION_SUBSCRIPTION
        )

    def _send_push(self, user_id: str, title: str, creator_id: str, video_id: str):
        """
        Production: call FCM/APNs API here.
        For demo: write to in-memory notification store.
        """
        notif = Notification(
            notif_id=str(uuid.uuid4()),
            user_id=user_id,
            creator_id=creator_id,
            video_id=video_id,
            title=title,
            sent_at=time.time(),
        )
        self.store.save(notif)

    def _handle_message(self, message):
        try:
            batch = json.loads(message.data.decode("utf-8"))
            user_ids   = batch["user_ids"]
            title      = batch["title"]
            creator_id = batch["creator_id"]
            video_id   = batch["video_id"]
            batch_id   = batch["batch_id"]

            # --- User preference filter (production = Redis cache) ---
            # opted_out = redis.smembers("notifications:disabled")
            # user_ids = [u for u in user_ids if u not in opted_out]

            for user_id in user_ids:
                self._send_push(user_id, title, creator_id, video_id)

            print(f"[{self.worker_id}] Sent {len(user_ids)} notifications "
                  f"for video='{title}' batch={batch_id[:8]}")
            message.ack()

        except Exception as e:
            print(f"[{self.worker_id}] ERROR processing batch: {e}")
            message.nack()   # Retried up to MAX_DELIVERY_ATTEMPTS, then → dead-letter

    def run(self):
        print(f"[{self.worker_id}] Listening on {self.sub_path} ...")
        flow_control = pubsub_v1.types.FlowControl(max_messages=50)
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
