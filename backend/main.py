from __future__ import annotations

import os
import sqlite3
import time
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from urllib.parse import quote
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
if __package__:
    from . import music
else:
    import music

BASE = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv('STUDYLOOM_DB', str(BASE / 'data' / 'studyloom.db')))
MEDIA = BASE / 'static'
ONLINE_SECONDS = 25

@contextmanager
def database():
    connection = sqlite3.connect(DB_PATH, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys=ON')
    try:
        with connection:
            yield connection
    finally:
        connection.close()

@asynccontextmanager
async def lifespan(app):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    with database() as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.executescript('''
        CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, token TEXT UNIQUE NOT NULL, name TEXT NOT NULL, color TEXT NOT NULL, last_seen REAL NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS focus_sessions (id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), started_at REAL NOT NULL, stopped_at REAL, duration_minutes INTEGER);
        CREATE UNIQUE INDEX IF NOT EXISTS one_active_focus ON focus_sessions(user_id) WHERE stopped_at IS NULL;
        CREATE TABLE IF NOT EXISTS stitches (id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), content TEXT NOT NULL, created_at REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS room_music (id INTEGER PRIMARY KEY CHECK(id=1), history TEXT NOT NULL, cursor INTEGER NOT NULL, started_at REAL NOT NULL, revision INTEGER NOT NULL);
        PRAGMA user_version=2;
        ''')
    yield

app = FastAPI(title='StudyLoom API', version='1.0.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(','), allow_methods=['GET', 'POST'], allow_headers=['Content-Type', 'X-User-Id'])
MEDIA.mkdir(parents=True, exist_ok=True)

class AudioStaticFiles(StaticFiles):
    def file_response(self, full_path, stat_result, scope, status_code=200):
        response = super().file_response(full_path, stat_result, scope, status_code)
        if Path(full_path).suffix.lower() in {'.mp3', '.flac', '.ogg', '.wav', '.m4a', '.aac'}:
            _, mime = music.metadata(str(full_path), stat_result.st_mtime_ns, stat_result.st_size)
            if mime:
                response.headers['content-type'] = mime
        return response

app.mount('/static', AudioStaticFiles(directory=MEDIA), name='media')

class Join(BaseModel):
    name: str = Field(default='同行者', min_length=1, max_length=20)

class StitchCreate(BaseModel):
    content: str = Field(min_length=1, max_length=180)

class MusicSkip(BaseModel):
    direction: Literal['previous', 'next']
    revision: int = Field(ge=0)

def member(db, token):
    user = db.execute('SELECT * FROM users WHERE token=?', (token,)).fetchone()
    if user is None:
        raise HTTPException(401, '访客身份已失效，请重新连接')
    return user

def session_json(row):
    return {**dict(row), 'started_at': datetime.fromtimestamp(row['started_at'], timezone.utc).isoformat(), 'stopped_at': datetime.fromtimestamp(row['stopped_at'], timezone.utc).isoformat() if row['stopped_at'] else None}

def tracks():
    result = []
    for path in sorted(MEDIA.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in {'.mp3', '.flac', '.ogg', '.wav', '.m4a', '.aac'}:
            continue
        if not path.resolve().is_relative_to(MEDIA.resolve()):
            continue
        title, separator, artist = path.stem.rpartition(' - ')
        subtitle = next((p for p in path.parent.iterdir() if p.stem == path.stem and p.suffix.lower() == '.lrc'), None)
        stat = path.stat()
        seconds = music.duration(str(path), stat.st_mtime_ns, stat.st_size)
        result.append({'id': path.relative_to(MEDIA).as_posix(), 'title': title if separator else path.stem, 'artist': artist if separator else '未知艺术家', 'album': '营地音乐库', 'audio_url': '/static/' + quote(path.relative_to(MEDIA).as_posix()), 'lyrics_url': '/static/' + quote(subtitle.relative_to(MEDIA).as_posix()) if subtitle else None, 'duration_seconds': seconds, 'position_seconds': 0, 'playing': False, 'white_noise': None, 'white_noise_volume': 0, 'next_dj': '', 'skip_votes': 0, 'votes_needed': 0})
    return result

@app.get('/api/health')
def health():
    with database() as db:
        db.execute('SELECT 1')
    return {'status': 'ok'}

@app.post('/api/users/join', status_code=201)
def join(payload: Join):
    name = payload.name.strip()
    if not name:
        raise HTTPException(422, '昵称不能为空')
    identity, token = str(uuid4()), str(uuid4()) + str(uuid4())
    with database() as db:
        db.execute('INSERT INTO users(id,token,name,color,last_seen) VALUES (?,?,?,?,?)', (identity, token, name, '#5f8e7d', time.time()))
    return {'id': identity, 'token': token, 'name': name}

@app.get('/api/tracks')
def library():
    return tracks()

@app.get('/api/music/current')
def current_music(x_user_id: str = Header(default='', alias='X-User-Id')):
    playlist = tracks()
    with database() as db:
        member(db, x_user_id)
        return music.snapshot(db, playlist)

@app.post('/api/music/skip')
def skip_music(payload: MusicSkip, x_user_id: str = Header(default='', alias='X-User-Id')):
    playlist = tracks()
    with database() as db:
        member(db, x_user_id)
        return music.snapshot(db, playlist, payload.direction, payload.revision)

@app.get('/api/rooms/current')
def room(x_user_id: str = Header(default='', alias='X-User-Id')):
    now = time.time()
    with database() as db:
        own = member(db, x_user_id)
        db.execute('UPDATE users SET last_seen=? WHERE id=?', (now, own['id']))
        online = db.execute('SELECT u.*, f.started_at FROM users u LEFT JOIN focus_sessions f ON f.user_id=u.id AND f.stopped_at IS NULL WHERE u.last_seen>? ORDER BY u.id', (now - ONLINE_SECONDS,)).fetchall()
        totals = db.execute('SELECT COALESCE(SUM(duration_minutes),0) FROM focus_sessions').fetchone()[0]
        own_total = db.execute('SELECT COALESCE(SUM(duration_minutes),0) FROM focus_sessions WHERE user_id=?', (own['id'],)).fetchone()[0]
        active = db.execute('SELECT * FROM focus_sessions WHERE user_id=? AND stopped_at IS NULL', (own['id'],)).fetchone()
        messages = db.execute('SELECT s.*,u.name,u.color FROM stitches s JOIN users u ON u.id=s.user_id ORDER BY created_at DESC LIMIT 100').fetchall()
    with database() as db:
        shared_track = music.snapshot(db, tracks())['track']
    return {'id': 'evening-breeze', 'name': '晚风自习室', 'member_count': len(online), 'max_members': 0, 'collective_minutes': totals, 'own_minutes': own_total, 'milestone_target_minutes': 2100, 'members': [{'id': u['id'], 'name': u['name'], 'initials': u['name'][0], 'color': u['color'], 'active': u['started_at'] is not None, 'active_minutes': int((now-u['started_at'])/60) if u['started_at'] else 0} for u in online], 'track': shared_track, 'active_session': session_json(active) if active else None, 'stitches': [{'id': s['id'], 'author_id': s['user_id'], 'author': s['name'], 'initials': s['name'][0], 'color': s['color'], 'content': s['content'], 'created_at': datetime.fromtimestamp(s['created_at'], timezone.utc).isoformat()} for s in messages]}

@app.post('/api/presence/leave')
def leave(x_user_id: str = Header(default='', alias='X-User-Id')):
    with database() as db:
        own = member(db, x_user_id)
        db.execute('UPDATE users SET last_seen=0 WHERE id=?', (own['id'],))
    return {'ok': True}

@app.post('/api/focus/start', status_code=201)
def start_focus(x_user_id: str = Header(default='', alias='X-User-Id')):
    with database() as db:
        own = member(db, x_user_id)
        identity = str(uuid4())
        try:
            db.execute('INSERT INTO focus_sessions(id,user_id,started_at) VALUES (?,?,?)', (identity, own['id'], time.time()))
        except sqlite3.IntegrityError:
            raise HTTPException(409, '已有进行中的专注，请重新连接恢复')
        return session_json(db.execute('SELECT * FROM focus_sessions WHERE id=?', (identity,)).fetchone())

@app.post('/api/focus/{session_id}/stop')
def stop_focus(session_id: str, x_user_id: str = Header(default='', alias='X-User-Id')):
    with database() as db:
        own = member(db, x_user_id)
        row = db.execute('SELECT * FROM focus_sessions WHERE id=? AND user_id=?', (session_id, own['id'])).fetchone()
        if row is None:
            raise HTTPException(404, '未找到这次专注')
        if row['stopped_at'] is None:
            now = time.time()
            db.execute('UPDATE focus_sessions SET stopped_at=?,duration_minutes=? WHERE id=? AND stopped_at IS NULL', (now, max(0, int((now-row['started_at']) // 60)), session_id))
        return session_json(db.execute('SELECT * FROM focus_sessions WHERE id=?', (session_id,)).fetchone())

@app.post('/api/stitches', status_code=201)
def create_stitch(payload: StitchCreate, x_user_id: str = Header(default='', alias='X-User-Id')):
    content = payload.content.strip()
    if not content:
        raise HTTPException(422, '留言不能为空')
    with database() as db:
        own = member(db, x_user_id)
        identity, now = str(uuid4()), time.time()
        db.execute('INSERT INTO stitches VALUES (?,?,?,?)', (identity, own['id'], content, now))
        return {'id': identity, 'author_id': own['id'], 'author': own['name'], 'initials': own['name'][0], 'color': own['color'], 'content': content, 'created_at': datetime.fromtimestamp(now, timezone.utc).isoformat()}

# Build the Vue app before starting production; API and media keep their own routes.
DIST = BASE.parent / 'frontend' / 'dist'
if DIST.is_dir():
    app.mount('/', StaticFiles(directory=DIST, html=True), name='frontend')
