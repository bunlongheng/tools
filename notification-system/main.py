"""
Demo Runner
===========
Runs the full pipeline end-to-end in a single process using threads
so you can see the flow without spinning up separate containers.

Sequence:
  1. Setup Pub/Sub topics + subscriptions
  2. Seed follower data (mock 10,000 followers for creator_A)
  3. Start FanoutWorker thread (listens for video-uploaded events)
  4. Start NotificationWorker threads x3 (compete for batches)
  5. Publish a video upload event
  6. Wait, then print stats
"""

import threading
import time

import setup_pubsub
from follower_store import FollowerStore
from notification_store import NotificationStore
from video_upload_service import VideoUploadService
from fanout_worker import FanoutWorker
from notification_worker import NotificationWorker


def main():
    # ── 1. Infra setup ──────────────────────────────────────────────
    setup_pubsub.setup()

    # ── 2. Shared stores ────────────────────────────────────────────
    follower_store    = FollowerStore()
    notification_store = NotificationStore()

    # Seed: creator_A has 10,000 followers
    # (scale this to 10_000_000 to simulate a big creator)
    NUM_FOLLOWERS = 10_000
    follower_store.seed("creator_A", NUM_FOLLOWERS)
    print(f"[Main] Seeded {NUM_FOLLOWERS:,} followers for creator_A\n")

    # ── 3. Start Fan-out worker ──────────────────────────────────────
    fanout_worker = FanoutWorker(follower_store)
    t_fanout = threading.Thread(target=fanout_worker.run, daemon=True)
    t_fanout.start()

    # ── 4. Start 3 Notification workers (horizontal scaling demo) ───
    notif_threads = []
    for i in range(1, 4):
        w = NotificationWorker(notification_store, worker_id=f"notif-worker-{i}")
        t = threading.Thread(target=w.run, daemon=True)
        t.start()
        notif_threads.append(t)

    time.sleep(1)   # Give workers time to start

    # ── 5. Simulate creator uploading a video ───────────────────────
    print("\n[Main] ── Creator uploads video ──────────────────────────\n")
    svc = VideoUploadService()
    svc.upload(
        creator_id="creator_A",
        video_id="vid_001",
        title="My Awesome New Video 🎬",
    )

    # ── 6. Wait for pipeline to drain ───────────────────────────────
    print("\n[Main] Waiting for pipeline to drain...\n")
    time.sleep(10)

    total = notification_store.total_sent()
    print(f"\n{'='*50}")
    print(f"  Total notifications delivered: {total:,} / {NUM_FOLLOWERS:,}")
    print(f"{'='*50}\n")

    # Show sample notifications for first user
    sample_user = f"user_creator_A_0"
    notifs = notification_store.get_for_user(sample_user)
    if notifs:
        n = notifs[0]
        print(f"Sample notification for {sample_user}:")
        print(f"  title      : {n.title}")
        print(f"  creator_id : {n.creator_id}")
        print(f"  video_id   : {n.video_id}")


if __name__ == "__main__":
    main()
