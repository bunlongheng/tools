"""
Creates all Pub/Sub topics and subscriptions.
Run once before starting workers.
"""

from google.cloud import pubsub_v1
from google.api_core.exceptions import AlreadyExists
import config

def create_topic(publisher, topic_path):
    try:
        publisher.create_topic(request={"name": topic_path})
        print(f"  [+] topic created: {topic_path}")
    except AlreadyExists:
        print(f"  [=] topic exists:  {topic_path}")

def create_subscription(subscriber, sub_path, topic_path, dead_letter_path=None, max_attempts=None):
    request = {"name": sub_path, "topic": topic_path}

    if dead_letter_path and max_attempts:
        request["dead_letter_policy"] = {
            "dead_letter_topic": dead_letter_path,
            "max_delivery_attempts": max_attempts,
        }
        request["retry_policy"] = {
            "minimum_backoff": {"seconds": 10},
            "maximum_backoff": {"seconds": 600},
        }

    try:
        subscriber.create_subscription(request=request)
        print(f"  [+] subscription created: {sub_path}")
    except AlreadyExists:
        print(f"  [=] subscription exists:  {sub_path}")


def setup():
    publisher  = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()

    video_topic  = publisher.topic_path(config.PROJECT_ID, config.VIDEO_UPLOADED_TOPIC)
    batch_topic  = publisher.topic_path(config.PROJECT_ID, config.NOTIFICATION_BATCH_TOPIC)
    dl_topic     = publisher.topic_path(config.PROJECT_ID, config.DEAD_LETTER_TOPIC)
    fanout_sub   = subscriber.subscription_path(config.PROJECT_ID, config.FANOUT_SUBSCRIPTION)
    notif_sub    = subscriber.subscription_path(config.PROJECT_ID, config.NOTIFICATION_SUBSCRIPTION)
    dl_sub       = subscriber.subscription_path(config.PROJECT_ID, "dead-letter-sub")

    print("\n=== Setting up Pub/Sub ===")

    # Topics
    create_topic(publisher, video_topic)
    create_topic(publisher, batch_topic)
    create_topic(publisher, dl_topic)

    # Subscriptions
    create_subscription(subscriber, fanout_sub, video_topic)
    create_subscription(
        subscriber, notif_sub, batch_topic,
        dead_letter_path=dl_topic,
        max_attempts=config.MAX_DELIVERY_ATTEMPTS
    )
    create_subscription(subscriber, dl_sub, dl_topic)

    print("=== Setup complete ===\n")


if __name__ == "__main__":
    setup()
