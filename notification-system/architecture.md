# System Design: Creator Video Upload Notification

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│  WRITE PATH  (1 event per video upload)                                  │
│                                                                           │
│   Creator                                                                 │
│     │                                                                     │
│     ▼                                                                     │
│  ┌──────────────────┐                                                     │
│  │  Video Upload    │  stores video metadata                              │
│  │  Service         │ ──────────────────────► Cloud Storage + Metadata DB │
│  │  (Cloud Run)     │                                                     │
│  └────────┬─────────┘                                                     │
│           │ publish 1 message                                             │
│           ▼                                                               │
│  ┌─────────────────────────┐                                              │
│  │  Pub/Sub Topic          │                                              │
│  │  "video-uploaded"       │                                              │
│  └─────────────────────────┘                                              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  FAN-OUT LAYER  (1 worker per video event → N batch messages)            │
│                                                                           │
│  ┌────────────────────────────────────────────────────────┐              │
│  │  Fan-out Worker  (Cloud Run Job, auto-scaled)           │              │
│  │                                                         │              │
│  │  1. Read creator_id from event                          │              │
│  │  2. Page through Follower DB in chunks of 500           │              │
│  │  3. Publish one Pub/Sub message per chunk               │              │
│  │                                                         │              │
│  │  10M followers ÷ 500 = 20,000 batch messages published  │              │
│  └───────┬─────────────────────────────────────┬───────────┘              │
│          │                                     │                          │
│          ▼                                     ▼                          │
│  ┌──────────────┐                   ┌──────────────────┐                  │
│  │ Follower DB  │                   │  Pub/Sub Topic   │                  │
│  │ (Cassandra / │                   │ "notification-   │                  │
│  │  Bigtable)   │                   │  batch"          │                  │
│  │              │                   │                  │                  │
│  │ PRIMARY KEY  │                   │ Each message =   │                  │
│  │ (creator_id, │                   │ {user_ids[500],  │                  │
│  │  follower_id)│                   │  video_id,       │                  │
│  └──────────────┘                   │  title}          │                  │
│                                     └──────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  NOTIFICATION DELIVERY LAYER  (horizontally scaled workers)              │
│                                                                           │
│         notification-batch topic                                          │
│              │         │         │                                        │
│         ─────┴─────────┴─────────┴─────  (Pub/Sub load-balances)         │
│         │                   │                   │                         │
│         ▼                   ▼                   ▼                         │
│   ┌──────────┐        ┌──────────┐        ┌──────────┐                   │
│   │ Notif    │        │ Notif    │        │ Notif    │  ... N replicas    │
│   │ Worker 1 │        │ Worker 2 │        │ Worker 3 │                   │
│   └────┬─────┘        └────┬─────┘        └────┬─────┘                   │
│        │                   │                   │                          │
│        └───────────────────┼───────────────────┘                          │
│                            │                                              │
│              ┌─────────────┼──────────────┐                              │
│              │             │              │                               │
│              ▼             ▼              ▼                               │
│         ┌─────────┐  ┌──────────┐  ┌──────────┐                         │
│         │  FCM /  │  │  Email   │  │  In-App  │                         │
│         │  APNs   │  │ (SES /   │  │  Inbox   │                         │
│         │  Push   │  │ SendGrid)│  │(Cassandra│                         │
│         └─────────┘  └──────────┘  └──────────┘                         │
│                                                                           │
│  Failed messages → Dead Letter Topic → alert + manual review             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

| Component | Technology | Role |
|-----------|-----------|------|
| Video Upload Service | Cloud Run | Accepts upload, publishes 1 event |
| `video-uploaded` topic | Pub/Sub | Decouples upload from fan-out |
| Fan-out Worker | Cloud Run Job | Pages followers, publishes batches |
| Follower DB | Cassandra / Bigtable | `(creator_id, follower_id)` → paginated reads |
| `notification-batch` topic | Pub/Sub | Load-balances work across N workers |
| Notification Workers | Cloud Run | Dispatch push/email/in-app |
| Preference Cache | Redis / Memorystore | Filter users who opted out |
| Dead Letter Topic | Pub/Sub | Catch failed messages after N retries |

---

## Message Flow (step by step)

```
1.  Creator uploads video
      → Video Upload Service stores it
      → publishes VideoUploadedEvent { creator_id, video_id, title }

2.  Fan-out Worker receives the event
      → queries Follower DB: page 0..N (500 users/page)
      → for each page, publishes NotificationBatch { user_ids[500], video_id, title }
      → acks original event only after all batches are published

3.  Pub/Sub delivers each NotificationBatch to ONE available Notification Worker
      (competing consumers — auto load-balanced)

4.  Notification Worker receives batch
      → checks Redis: filter opted-out users
      → calls FCM for push notifications
      → writes to in-app inbox (Cassandra)
      → acks message on success / nacks on failure (→ retry with backoff)

5.  After MAX_DELIVERY_ATTEMPTS failures → message goes to Dead Letter Topic
      → alert fires → on-call team investigates
```

---

## Scaling Numbers

```
Creator followers: 100,000,000  (100M)
Batch size:              500
─────────────────────────────────
Batch messages:      200,000    published per video upload

Notification workers:    500    replicas (Cloud Run auto-scale)
Batches per worker:      400
Users per worker:    200,000

Throughput per worker:  ~1,000 push/sec (FCM limit)
Time to notify 100M:     ~200 seconds   (~3 min end-to-end)
```

---

## Key Design Decisions

### 1. Two-tier fan-out (not one giant loop)
- Upload service publishes **1 message** — fast, no follower lookups at upload time
- Fan-out worker handles the N-to-M explosion asynchronously

### 2. Batching (500 users/message)
- Avoids 100M individual Pub/Sub messages (cost + throughput limits)
- Each batch message is independently retry-able

### 3. Competing consumers on `notification-batch`
- Pub/Sub delivers each message to exactly **one** subscriber
- Add more workers → linear throughput increase

### 4. Dead Letter Topic
- After 5 failed delivery attempts, message is moved to DLT
- Prevents poison pills from blocking the queue

### 5. Follower DB schema
- Cassandra `PRIMARY KEY (creator_id, follower_id)` → efficient paginated scans
- Fan-out worker never loads all followers into RAM — streams pages

### 6. User preference filtering
- Redis cache: `SET notifications:disabled` per user
- Checked inside Notification Worker **before** calling FCM
- Saves FCM quota and respects user opt-outs

---

## Running Locally

```bash
# 1. Start Pub/Sub emulator
docker compose up -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the demo (setup + seed + publish + workers all in one)
python main.py
```

Expected output:
```
=== Setting up Pub/Sub ===
  [+] topic created: video-uploaded
  [+] topic created: notification-batch
  [+] subscription created: fanout-worker-sub
  ...

[Main] Seeded 10,000 followers for creator_A

[VideoUploadService] Published event → creator=creator_A video=vid_001
[FanoutWorker] creator=creator_A followers=10,000 → fanning out...
[FanoutWorker] Done — published 20 batches (10,000 notifications enqueued)
[notif-worker-1] Sent 500 notifications for video='My Awesome New Video 🎬'
[notif-worker-2] Sent 500 notifications for video='My Awesome New Video 🎬'
...

==================================================
  Total notifications delivered: 10,000 / 10,000
==================================================
```
