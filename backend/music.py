"""A persisted room radio clock shared across processes and visitors."""
import json
import secrets
import time
from functools import lru_cache

from mutagen import File
from mutagen.mp3 import MP3


@lru_cache(maxsize=256)
def metadata(path: str, modified_ns: int, size: int) -> tuple[float, str | None]:
    try:
        try:
            media = File(path)
        except Exception:
            # Some supplied .flac files contain MPEG frames; inspect the bytes.
            media = MP3(path)
        if media is not None and media.info.length > 0:
            return float(media.info.length), 'audio/mpeg' if isinstance(media, MP3) else media.mime[0]
    except Exception:
        pass
    return 0, None


def duration(path: str, modified_ns: int, size: int) -> float:
    return metadata(path, modified_ns, size)[0]


def snapshot(db, playlist, direction=None, expected_revision=None):
    # Serialise automatic advancement and skip commands, including multiple workers.
    db.execute('BEGIN IMMEDIATE')
    now = time.time()
    available = {track['id']: track for track in playlist if track['duration_seconds'] > 0}
    row = db.execute('SELECT * FROM room_music WHERE id=1').fetchone()
    history = json.loads(row['history']) if row else []
    cursor = row['cursor'] if row else 0
    started = row['started_at'] if row else now
    revision = row['revision'] if row else 0

    def advance(at):
        nonlocal history, cursor, started, revision
        current = history[cursor] if history else None
        choices = [key for key in available if key != current] or list(available)
        history = history[:cursor + 1] if history else []
        history.append(secrets.choice(choices))
        history = history[-100:]
        cursor = len(history) - 1
        started = at
        revision += 1

    if available:
        if not history or history[cursor] not in available:
            advance(now)
        # Carry elapsed time into the next random song rather than resetting on a poll.
        for _ in range(100):
            end = started + available[history[cursor]]['duration_seconds']
            if end > now:
                break
            advance(end)
        else:
            advance(now)
        # A stale command cannot skip the freshly changed song a second time.
        if direction and expected_revision == revision:
            if direction == 'previous' and cursor > 0 and history[cursor - 1] in available:
                cursor -= 1
                started = now
                revision += 1
            else:
                advance(now)
        db.execute('INSERT INTO room_music VALUES (1,?,?,?,?) ON CONFLICT(id) DO UPDATE SET history=excluded.history,cursor=excluded.cursor,started_at=excluded.started_at,revision=excluded.revision',
                   (json.dumps(history), cursor, started, revision))
        track = {**available[history[cursor]], 'position_seconds': max(0, now - started), 'playing': True}
    else:
        track = None
    return {'track': track, 'revision': revision, 'server_time': now, 'started_at': started, 'can_previous': bool(cursor > 0), 'library_count': len(available)}
