import os

# Pub/Sub emulator (set for local dev)
os.environ.setdefault("PUBSUB_EMULATOR_HOST", "localhost:8085")

PROJECT_ID = "demo-project"

# Topics
VIDEO_UPLOADED_TOPIC    = "video-uploaded"
NOTIFICATION_BATCH_TOPIC = "notification-batch"
DEAD_LETTER_TOPIC        = "notification-dead-letter"

# Subscriptions
FANOUT_SUBSCRIPTION        = "fanout-worker-sub"
NOTIFICATION_SUBSCRIPTION  = "notification-worker-sub"

# Fan-out config
FOLLOWER_BATCH_SIZE = 500       # users per Pub/Sub message
MAX_DELIVERY_ATTEMPTS = 5       # before dead-letter
