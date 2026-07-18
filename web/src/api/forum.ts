// web/src/api/forum.ts — 08-forum-community F5: forum feed/thread/vote/profile API client.
// Same pattern as wanted.ts: Bearer session client (client.ts), envelope unwrapped locally.
import { api, ApiError } from './client'

export interface Envelope<T> {
  ok: boolean
  data: T | null
  error: string | null
  meta: Record<string, unknown> | null
}

async function unwrap<T>(promise: Promise<Envelope<T>>): Promise<{ data: T; meta: Record<string, unknown> }> {
  const body = await promise
  if (!body.ok || body.data === null) {
    throw new ApiError(200, body.error ?? 'unknown error')
  }
  return { data: body.data, meta: body.meta ?? {} }
}

export type ThreadType = 'discussion' | 'price_check'

export interface ThreadSummary {
  thread_ulid: string
  title: string
  author_user_ulid: string
  province_code: string | null
  thread_type: ThreadType
  created_at: string
  last_reply_at: string
  reply_count: number
  net_votes: number
  verified_anchor_count: number
  rank_score?: number
}

export interface PostAnchor {
  anchor_ulid: string
  anchor_type: 'vehicle' | 'entity' | 'province'
  anchor_ref: string
  snapshot: Record<string, unknown>
  verified: boolean
}

export interface ForumPost {
  post_ulid: string
  author_user_ulid: string
  body: string
  is_first_post: boolean
  created_at: string
  net_votes: number
  anchors: PostAnchor[]
}

export interface ThreadDetail extends ThreadSummary {
  posts: ForumPost[]
}

export interface AnchorCandidate {
  anchor_type: 'vehicle' | 'entity'
  anchor_ref: string
  label: string
  price?: number | null
  deep_link?: string | null
}

export interface UserProfile {
  user_ulid: string
  name: string | null
  role: string
  member_since: string
  reputation: number
  reputation_breakdown: { reason: string; total: number; count: number }[]
  thread_count: number
  post_count: number
  wanted_count: number
}

export interface AnchorInput {
  anchor_type: 'vehicle' | 'entity' | 'province'
  anchor_ref: string
}

export const forumApi = {
  threads: (opts: { sort?: 'hot' | 'recent'; province?: string; page?: number; size?: number } = {}) =>
    unwrap<ThreadSummary[]>(
      api.get<Envelope<ThreadSummary[]>>(
        `/forum/threads?sort=${opts.sort ?? 'hot'}${opts.province ? `&province=${opts.province}` : ''}&page=${opts.page ?? 1}&size=${opts.size ?? 30}`,
      ),
    ),
  thread: (threadUlid: string) => unwrap<ThreadDetail>(api.get<Envelope<ThreadDetail>>(`/forum/threads/${threadUlid}`)),
  createThread: (payload: { title: string; body: string; thread_type?: ThreadType; province_code?: string | null; anchors?: AnchorInput[] }) =>
    unwrap<ThreadSummary & { first_post_ulid: string }>(api.post('/forum/threads', payload)),
  reply: (threadUlid: string, payload: { body: string; anchors?: AnchorInput[] }) =>
    unwrap<{ post_ulid: string; thread_ulid: string }>(api.post(`/forum/threads/${threadUlid}/posts`, payload)),
  vote: (postUlid: string, value: -1 | 0 | 1) =>
    unwrap<{ post_ulid: string; net_votes: number; your_vote: number }>(
      api.post(`/forum/posts/${postUlid}/vote`, { value }),
    ),
  flag: (postUlid: string, reason?: string) =>
    unwrap<{ post_ulid: string; flagged: boolean }>(api.post(`/forum/posts/${postUlid}/flag`, { reason })),
  anchorSearch: (q: string, kind: 'vehicle' | 'entity' = 'vehicle') =>
    unwrap<AnchorCandidate[]>(api.get<Envelope<AnchorCandidate[]>>(`/forum/anchor-search?q=${encodeURIComponent(q)}&kind=${kind}`)),
  profile: (userUlid: string) => unwrap<UserProfile>(api.get<Envelope<UserProfile>>(`/forum/users/${userUlid}`)),
}
