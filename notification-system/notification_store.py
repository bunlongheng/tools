"""
Mock notification store (production = Cassandra or DynamoDB).

Schema:
  CREATE TABLE notifications (
    user_id   TEXT,
    notif_id  UUID,
    creator_id TEXT,
    video_id  TEXT,
    title     TEXT,
    sent_at   TIMESTAMP,
    PRIMARY KEY (user_id, sent_at)
  ) WITH CLUSTERING ORDER BY (sent_at DESC);
"""

import time
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Notification:
    notif_id: str
    user_id: str
    creator_id: str
    video_id: str
    title: str
    sent_at: float


class NotificationStore:
    def __init__(self):
        self._data: dict[str, list[Notification]] = defaultdict(list)

    def save(self, notif: Notification):
        self._data[notif.user_id].append(notif)

    def get_for_user(self, user_id: str) -> list[Notification]:
        return sorted(self._data[user_id], key=lambda n: n.sent_at, reverse=True)

    def total_sent(self) -> int:
        return sum(len(v) for v in self._data.values())
