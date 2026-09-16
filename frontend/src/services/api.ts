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
  id: string
  audio_url: string
  lyrics_url: string | null
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
  track: ApiTrack | null
  active_session: FocusSession | null
  stitches: ApiStitch[]
}

export type FocusSession = {
  id: string
  user_id: string
  started_at: string
  stopped_at: string | null
  duration_minutes: number | null
}

export type MusicState = {
  track: ApiTrack | null
  revision: number
  server_time: number
  started_at: number
  can_previous: boolean
  library_count: number
  received_at: number
  transit_seconds: number
}

async function musicRequest(path: string, init?: RequestInit): Promise<MusicState> {
  await ensureIdentity()
  const sent = performance.now()
  const state = await request<MusicState>(path, init)
  const received = performance.now()
  return { ...state, received_at: received, transit_seconds: (received - sent) / 2000 }
}

export const identity = { id: localStorage.getItem('studyloom-user-id') ?? '', token: localStorage.getItem('studyloom-token') ?? '' }
let joining: Promise<void> | null = null
export async function ensureIdentity() {
  if (identity.token) return
  if (!joining) joining = joinIdentity().finally(() => { joining = null })
  await joining
}
async function joinIdentity() {
  if (identity.token) return
  const response = await fetch('/api/users/join', { signal: AbortSignal.timeout(10000), method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: localStorage.getItem('studyloom-name') || `同行者${Math.floor(Math.random() * 9000 + 1000)}` }) })
  if (!response.ok) {
    if (response.status === 404) throw new Error('后端版本不匹配：请重启后端以加载加入房间接口')
    const body = await response.json().catch(() => ({}))
    const detail = typeof body.detail === 'string' ? body.detail : '请检查后端服务与昵称设置'
    throw new Error(`无法加入房间（${response.status}）：${detail}`)
  }
  const user = await response.json()
  identity.id = user.id
  identity.token = user.token
  localStorage.setItem('studyloom-user-id', user.id)
  localStorage.setItem('studyloom-token', user.token)
  localStorage.setItem('studyloom-name', user.name)
}
export function leaveRoom() {
  void fetch('/api/presence/leave', { method: 'POST', headers: { 'X-User-Id': identity.token }, keepalive: true }).catch(() => {})
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  await ensureIdentity()
  const response = await fetch(path, { signal: AbortSignal.timeout(10000), ...init, headers: { 'Content-Type': 'application/json', 'X-User-Id': identity.token, ...init?.headers } })
  if (response.status === 401) {
    identity.token = ''
    localStorage.removeItem('studyloom-token')
    throw new Error('身份已失效，请重新连接')
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail ?? `请求失败（${response.status}）`)
  }
  return response.json() as Promise<T>
}

export const studyLoomApi = {
  music: () => musicRequest('/api/music/current'),
  skipMusic: (direction: 'previous' | 'next', revision: number) => musicRequest('/api/music/skip', { method: 'POST', body: JSON.stringify({ direction, revision }) }),
  tracks: () => request<ApiTrack[]>('/api/tracks'),
  room: () => request<RoomSnapshot>('/api/rooms/current'),
  startFocus: () => request<FocusSession>('/api/focus/start', { method: 'POST' }),
  stopFocus: (sessionId: string) => request<FocusSession>(`/api/focus/${sessionId}/stop`, { method: 'POST' }),
  createStitch: (content: string) => request<ApiStitch>('/api/stitches', { method: 'POST', body: JSON.stringify({ content }) }),
}
