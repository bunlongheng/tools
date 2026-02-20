"""
Mock follower store (production = Cassandra or Bigtable).

Schema (Cassandra-style):
  CREATE TABLE followers (
    creator_id TEXT,
    follower_id TEXT,
    followed_at TIMESTAMP,
    PRIMARY KEY (creator_id, follower_id)
  ) WITH CLUSTERING ORDER BY (follower_id ASC);

Reads are paginated so fan-out never loads all IDs into RAM at once.
"""

from typing import Generator, List


class FollowerStore:
    def __init__(self):
        # In-memory: {creator_id: [user_id, ...]}
        self._data: dict[str, list[str]] = {}

    def seed(self, creator_id: str, num_followers: int):
        """Seed mock followers (e.g. 10M for a big creator)."""
        self._data[creator_id] = [
            f"user_{creator_id}_{i}" for i in range(num_followers)
        ]

    def get_followers_page(self, creator_id: str, page: int, page_size: int) -> List[str]:
        followers = self._data.get(creator_id, [])
        start = page * page_size
        return followers[start : start + page_size]

    def iter_followers(self, creator_id: str, batch_size: int) -> Generator[List[str], None, None]:
        """Yield follower ID batches one page at a time — never pulls all into RAM."""
        page = 0
        while True:
            batch = self.get_followers_page(creator_id, page, batch_size)
            if not batch:
                break
            yield batch
            page += 1

    def count(self, creator_id: str) -> int:
        return len(self._data.get(creator_id, []))
