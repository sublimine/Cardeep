// web/src/pages/CommunityThread.tsx — 08-forum-community F5: "/community/thread/:id"
// (carta §6.3). Anchor cards + composer with DataLinker (search real inventory, never
// paste a URL) + optimistic vote with rollback on server rejection.
import { useCallback, useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowBigUp, ArrowBigDown, X, Flag, User as UserIcon } from 'lucide-react'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import { Badge } from '../components/Badge'
import { PageSkeleton } from '../components/LoadingSpinner'
import { useToast } from '../components/Toast'
import { ApiError } from '../api/client'
import { forumApi, type ThreadDetail, type ForumPost, type AnchorInput } from '../api/forum'
import { AnchorCard } from '../components/forum/AnchorCards'
import { DataLinker } from '../components/forum/DataLinker'

function errorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    try {
      const parsed = JSON.parse(err.message) as { detail?: string }
      if (parsed.detail) return parsed.detail
    } catch { /* raw text */ }
    return err.message
  }
  return err instanceof Error ? err.message : 'Error desconocido'
}

function Composer({ threadUlid, onPosted }: { threadUlid: string; onPosted: () => void }) {
  const { error: toastErr, success } = useToast()
  const [body, setBody] = useState('')
  const [anchors, setAnchors] = useState<AnchorInput[]>([])
  const [submitting, setSubmitting] = useState(false)

  const submit = useCallback(async () => {
    if (!body.trim()) return
    setSubmitting(true)
    try {
      await forumApi.reply(threadUlid, { body: body.trim(), anchors })
      setBody(''); setAnchors([])
      success('Respuesta publicada')
      onPosted()
    } catch (err) {
      toastErr(errorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }, [body, anchors, threadUlid, success, toastErr, onPosted])

  return (
    <Card className="mb-4">
      <textarea
        className="w-full rounded-md p-3 text-sm"
        style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', color: 'var(--text-primary)' }}
        rows={3}
        placeholder="Escribe una respuesta…"
        value={body}
        onChange={(e) => setBody(e.target.value)}
      />
      {anchors.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2">
          {anchors.map((a, i) => (
            <span key={`${a.anchor_type}-${a.anchor_ref}`} className="inline-flex items-center gap-1 rounded-full px-2 py-1 text-[11px]" style={{ background: 'var(--bg-surface)', color: 'var(--text-secondary)' }}>
              {a.anchor_ref}
              <button onClick={() => setAnchors((prev) => prev.filter((_, idx) => idx !== i))}><X className="h-3 w-3" /></button>
            </span>
          ))}
        </div>
      )}
      <div className="mt-2.5 flex items-center justify-between">
        <DataLinker onSelect={(a) => setAnchors((prev) => [...prev, a])} />
        <Button size="sm" onClick={submit} loading={submitting}>Responder</Button>
      </div>
    </Card>
  )
}

function PostCard({ post, onChanged }: { post: ForumPost; onChanged: () => void }) {
  const { error: toastErr } = useToast()
  const [localVote, setLocalVote] = useState(0)
  const [localNet, setLocalNet] = useState(post.net_votes)

  const vote = useCallback(async (value: -1 | 0 | 1) => {
    const nextVote = localVote === value ? 0 : value
    const prevNet = localNet
    const prevVote = localVote
    // optimistic update with rollback (carta §6.3: "voto optimista con rollback visible")
    setLocalNet(prevNet - prevVote + nextVote)
    setLocalVote(nextVote)
    try {
      const { data } = await forumApi.vote(post.post_ulid, nextVote as -1 | 0 | 1)
      setLocalNet(data.net_votes)
    } catch (err) {
      setLocalNet(prevNet)
      setLocalVote(prevVote)
      toastErr(errorMessage(err))
    }
  }, [localVote, localNet, post.post_ulid, toastErr])

  const flag = useCallback(async () => {
    try {
      await forumApi.flag(post.post_ulid)
      toastErr('Post reportado a moderación')
      onChanged()
    } catch (err) {
      toastErr(errorMessage(err))
    }
  }, [post.post_ulid, onChanged, toastErr])

  return (
    <Card className="mb-3">
      <div className="flex gap-3">
        <div className="flex shrink-0 flex-col items-center gap-0.5">
          <button onClick={() => vote(1)}><ArrowBigUp className="h-5 w-5" fill={localVote === 1 ? '#3b82f6' : 'none'} style={{ color: localVote === 1 ? '#3b82f6' : 'var(--text-muted)' }} /></button>
          <span className="text-[12px] font-bold" style={{ color: 'var(--text-primary)' }}>{localNet}</span>
          <button onClick={() => vote(-1)}><ArrowBigDown className="h-5 w-5" fill={localVote === -1 ? '#ef4444' : 'none'} style={{ color: localVote === -1 ? '#ef4444' : 'var(--text-muted)' }} /></button>
        </div>
        <div className="min-w-0 flex-1">
          <div className="mb-1.5 flex items-center gap-2 text-[11px]" style={{ color: 'var(--text-muted)' }}>
            <UserIcon className="h-3 w-3" />
            <Link to={`/community/user/${post.author_user_ulid}`} className="hover:underline">{post.author_user_ulid.slice(0, 10)}</Link>
            · {new Date(post.created_at).toLocaleString('es-ES')}
          </div>
          <p className="whitespace-pre-wrap text-[13px]" style={{ color: 'var(--text-primary)' }}>{post.body}</p>
          {post.anchors.length > 0 && (
            <div className="mt-3 space-y-2">
              {post.anchors.map((a) => <AnchorCard key={a.anchor_ulid} anchor={a} />)}
            </div>
          )}
          <button onClick={flag} className="mt-2 inline-flex items-center gap-1 text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
            <Flag className="h-3 w-3" /> Reportar
          </button>
        </div>
      </div>
    </Card>
  )
}

export default function CommunityThread() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [thread, setThread] = useState<ThreadDetail | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    if (!id) return
    try {
      const { data } = await forumApi.thread(id)
      setThread(data)
    } catch {
      setThread(null)
    }
  }, [id])

  useEffect(() => {
    setLoading(true)
    load().finally(() => setLoading(false))
  }, [load])

  if (loading) return <PageSkeleton />
  if (!thread) {
    return (
      <div style={{ padding: '24px 28px' }}>
        <EmptyState title="Hilo no encontrado" message="Puede haber sido eliminado." action={<Button onClick={() => navigate('/community')}>Volver al foro</Button>} />
      </div>
    )
  }

  return (
    <div className="mx-auto p-[20px_24px_48px]" style={{ maxWidth: 900 }}>
      <div className="mb-4">
        <div className="flex items-center gap-2">
          <h1 className="text-[19px] font-bold" style={{ color: 'var(--text-primary)' }}>{thread.title}</h1>
          {thread.thread_type === 'price_check' && <Badge color="blue">¿Buen precio?</Badge>}
        </div>
        <div className="mt-1 text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
          {thread.reply_count} respuestas · {thread.province_code ?? 'sin provincia'}
        </div>
      </div>

      {thread.posts.map((p) => <PostCard key={p.post_ulid} post={p} onChanged={load} />)}

      <Composer threadUlid={thread.thread_ulid} onPosted={load} />
    </div>
  )
}
