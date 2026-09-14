export type ApiMember = {
  id: string
  name: string
  initials: string
  color: string
  active: boolean
  active_minutes: number
}

export type ApiStitch = {
  id: string
  author_id: string
  author: string
  initials: string
  color: string
  content: string
  created_at: string
}

export type ApiTrack = {
  title: string
  artist: string
  album: string
  duration_seconds: number
  position_seconds: number
  playing: boolean
  white_noise: string | null
  white_noise_volume: number
  next_dj: string
  skip_votes: number
  votes_needed: number
}

export type RoomSnapshot = {
  id: string
  name: string
  member_count: number
  max_members: number
  collective_minutes: number
  own_minutes: number
  milestone_target_minutes: number
  members: ApiMember[]
  track: ApiTrack
  stitches: ApiStitch[]
}

export type FocusSession = {
  id: string
  user_id: string
  started_at: string
  stopped_at: string | null
  duration_minutes: number | null
}

const headers = { 'Content-Type': 'application/json', 'X-User-Id': 'member-you' }

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, { ...init, headers: { ...headers, ...init?.headers } })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ?? `请求失败（${response.status}）`)
  }
  return response.json() as Promise<T>
}

export const studyLoomApi = {
  room: () => request<RoomSnapshot>('/api/rooms/current'),
  startFocus: () => request<FocusSession>('/api/focus/start', { method: 'POST' }),
  stopFocus: (sessionId: string) => request<FocusSession>(`/api/focus/${sessionId}/stop`, { method: 'POST' }),
  createStitch: (content: string) => request<ApiStitch>('/api/stitches', { method: 'POST', body: JSON.stringify({ content }) }),
}
