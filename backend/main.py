from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="StudyLoom API", description="Private room APIs for the StudyLoom MVP.", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-User-Id"],
)

UserId = Annotated[str, Header(alias="X-User-Id")]
ROOM_ID = "evening-breeze"
MAX_ROOM_MEMBERS = 20


class Member(BaseModel):
    id: str
    name: str
    initials: str
    color: str
    active: bool = False
    active_minutes: int = 0


class Track(BaseModel):
    title: str
    artist: str
    album: str
    duration_seconds: int
    position_seconds: int
    playing: bool
    white_noise: str | None = None
    white_noise_volume: int = 0
    next_dj: str
    skip_votes: int = 0
    votes_needed: int = 5


class Stitch(BaseModel):
    id: str
    author_id: str
    author: str
    initials: str
    color: str
    content: str
    created_at: datetime


class RoomSnapshot(BaseModel):
    id: str
    name: str
    member_count: int
    max_members: int
    collective_minutes: int
    own_minutes: int
    milestone_target_minutes: int
    members: list[Member]
    track: Track
    stitches: list[Stitch]


class FocusSession(BaseModel):
    id: str
    user_id: str
    started_at: datetime
    stopped_at: datetime | None = None
    duration_minutes: int | None = None


class StitchCreate(BaseModel):
    content: str = Field(min_length=1, max_length=180)


MEMBERS: dict[str, Member] = {
    "member-rain": Member(id="member-rain", name="小雨", initials="雨", color="#ef7f5a", active=True, active_minutes=42),
    "member-he": Member(id="member-he", name="阿禾", initials="禾", color="#5f8e7d", active=True, active_minutes=18),
    "member-lin": Member(id="member-lin", name="Lin", initials="L", color="#7789b5", active=True, active_minutes=60),
    "member-you": Member(id="member-you", name="你", initials="你", color="#b07d9f"),
}
MEMBER_TOTALS = {"member-rain": 520, "member-he": 460, "member-lin": 720, "member-you": 268}
TRACK = Track(
    title="夜空中最亮的星", artist="逃跑计划", album="世界", duration_seconds=284,
    position_seconds=136, playing=True, white_noise="雨声", white_noise_volume=30,
    next_dj="Lin", skip_votes=2, votes_needed=5,
)
STITCHES: list[Stitch] = [
    Stitch(id="stitch-1", author_id="member-he", author="阿禾", initials="禾", color="#5f8e7d", content="图书馆今晚很安静，适合把最后两章收尾。", created_at=datetime(2026, 9, 14, 21, 6, tzinfo=timezone.utc)),
    Stitch(id="stitch-2", author_id="member-rain", author="小雨", initials="雨", color="#ef7f5a", content="刚做完一套题，先休息十分钟。你们也加油 🧵", created_at=datetime(2026, 9, 14, 20, 42, tzinfo=timezone.utc)),
]
FOCUS_SESSIONS: dict[str, FocusSession] = {}
STATE_LOCK = Lock()


def get_member(user_id: str) -> Member:
    member = MEMBERS.get(user_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="邀请码成员身份无效")
    return member


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/rooms/current", response_model=RoomSnapshot)
async def current_room(x_user_id: UserId = "member-you") -> RoomSnapshot:
    get_member(x_user_id)
    # Privacy boundary: totals for other individual members never leave this endpoint.
    return RoomSnapshot(
        id=ROOM_ID, name="晚风自习室", member_count=len(MEMBERS), max_members=MAX_ROOM_MEMBERS,
        collective_minutes=sum(MEMBER_TOTALS.values()), own_minutes=MEMBER_TOTALS[x_user_id],
        milestone_target_minutes=2100, members=list(MEMBERS.values()), track=TRACK, stitches=STITCHES,
    )


@app.post("/api/focus/start", response_model=FocusSession, status_code=status.HTTP_201_CREATED)
async def start_focus(x_user_id: UserId = "member-you") -> FocusSession:
    member = get_member(x_user_id)
    with STATE_LOCK:
        active = next((session for session in FOCUS_SESSIONS.values() if session.user_id == x_user_id and session.stopped_at is None), None)
        if active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="已有进行中的编织")
        session = FocusSession(id=str(uuid4()), user_id=x_user_id, started_at=datetime.now(timezone.utc))
        FOCUS_SESSIONS[session.id] = session
        member.active = True
        member.active_minutes = 0
        return session


@app.post("/api/focus/{session_id}/stop", response_model=FocusSession)
async def stop_focus(session_id: str, x_user_id: UserId = "member-you") -> FocusSession:
    member = get_member(x_user_id)
    with STATE_LOCK:
        session = FOCUS_SESSIONS.get(session_id)
        if session is None or session.user_id != x_user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到这次编织")
        if session.stopped_at is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="这次编织已经结束")
        stopped_at = datetime.now(timezone.utc)
        seconds = max(0, int((stopped_at - session.started_at).total_seconds()))
        duration_minutes = max(1, (seconds + 59) // 60)
        session.stopped_at = stopped_at
        session.duration_minutes = duration_minutes
        MEMBER_TOTALS[x_user_id] += duration_minutes
        member.active = False
        member.active_minutes = 0
        return session


@app.post("/api/stitches", response_model=Stitch, status_code=status.HTTP_201_CREATED)
async def create_stitch(payload: StitchCreate, x_user_id: UserId = "member-you") -> Stitch:
    member = get_member(x_user_id)
    stitch = Stitch(
        id=str(uuid4()), author_id=member.id, author=member.name, initials=member.initials,
        color=member.color, content=payload.content.strip(), created_at=datetime.now(timezone.utc),
    )
    if not stitch.content:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="针脚内容不能为空")
    with STATE_LOCK:
        STITCHES.insert(0, stitch)
    return stitch
