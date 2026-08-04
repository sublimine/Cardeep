// web/src/pages/CommunityThread.tsx — 08-forum-community F5: "/community/thread/:id"
// (carta §6.3). Anchor cards + composer with DataLinker (search real inventory, never
// paste a URL) + optimistic vote with rollback on server rejection.
import { useCallback, useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
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
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
      <Card className="mb-4">
        <textarea
          className="w-full rounded-md p-3 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-accent-blue/30"
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
                <button
                  onClick={() => setAnchors((prev) => prev.filter((_, idx) => idx !== i))}
                  className="rounded-full transition-colors hover:text-[var(--c-rose)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
                  aria-label="Quitar dato vinculado"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        )}
        <div className="mt-2.5 flex items-center justify-between">
          <DataLinker onSelect={(a) => setAnchors((prev) => [...prev, a])} />
          <Button size="sm" onClick={submit} loading={submitting}>Responder</Button>
        </div>
      </Card>
    </motion.div>
  )
}

function PostCard({ post, onChanged, index = 0 }: { post: ForumPost; onChanged: () => void; index?: number }) {
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
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: Math.min(index, 10) * 0.04 }}
    >
      <Card className="mb-3">
        <div className="flex gap-3">
          <div className="flex shrink-0 flex-col items-center gap-0.5">
            <motion.button
              whileHover={{ scale: 1.15 }}
              whileTap={{ scale: 0.9 }}
              transition={{ type: 'spring', stiffness: 420, damping: 22 }}
              onClick={() => vote(1)}
              className="rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
              aria-label="Voto a favor"
              aria-pressed={localVote === 1}
            >
              <ArrowBigUp className="h-5 w-5" fill={localVote === 1 ? 'currentColor' : 'none'} style={{ color: localVote === 1 ? 'var(--c-brand)' : 'var(--text-muted)' }} />
            </motion.button>
            <span className="font-mono text-[12px] font-bold tabular-nums" style={{ color: 'var(--text-primary)' }}>{localNet}</span>
            <motion.button
              whileHover={{ scale: 1.15 }}
              whileTap={{ scale: 0.9 }}
              transition={{ type: 'spring', stiffness: 420, damping: 22 }}
              onClick={() => vote(-1)}
              className="rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
              aria-label="Voto en contra"
              aria-pressed={localVote === -1}
            >
              <ArrowBigDown className="h-5 w-5" fill={localVote === -1 ? 'currentColor' : 'none'} style={{ color: localVote === -1 ? 'var(--c-rose)' : 'var(--text-muted)' }} />
            </motion.button>
          </div>
          <div className="min-w-0 flex-1">
            <div className="mb-1.5 flex items-center gap-2 text-[11px]" style={{ color: 'var(--text-muted)' }}>
              <UserIcon className="h-3 w-3" />
              <Link
                to={`/community/user/${post.author_user_ulid}`}
                className="rounded transition-colors hover:text-[var(--text-primary)] hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
              >
                {post.author_user_ulid.slice(0, 10)}
              </Link>
              {/* carta §4.7 (PistonHeads-exact): el rol se muestra SIEMPRE, dealer vs particular */}
              {post.author_role && (
                <Badge color={post.author_role === 'dealer' ? 'blue' : post.author_role === 'staff' ? 'purple' : 'gray'}>
                  {post.author_role}
                </Badge>
              )}
              · <span className="tabular-nums">{new Date(post.created_at).toLocaleString('es-ES')}</span>
            </div>
            <p className="whitespace-pre-wrap text-[13px]" style={{ color: 'var(--text-primary)' }}>{post.body}</p>
            {post.anchors.length > 0 && (
              <div className="mt-3 space-y-2">
                {post.anchors.map((a) => <AnchorCard key={a.anchor_ulid} anchor={a} />)}
              </div>
            )}
            <button
              onClick={flag}
              className="mt-2 inline-flex items-center gap-1 rounded text-[10.5px] transition-colors hover:text-[var(--c-rose)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
              style={{ color: 'var(--text-muted)' }}
            >
              <Flag className="h-3 w-3" /> Reportar
            </button>
          </div>
        </div>
      </Card>
    </motion.div>
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
      <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="mb-4">
        <div className="flex items-center gap-2">
          <h1 className="text-[19px] font-bold" style={{ color: 'var(--text-primary)' }}>{thread.title}</h1>
          {thread.thread_type === 'price_check' && <Badge color="blue">¿Buen precio?</Badge>}
        </div>
        <div className="mt-1 text-[11.5px] tabular-nums" style={{ color: 'var(--text-muted)' }}>
          {thread.reply_count} respuestas · {thread.province_code ?? 'sin provincia'}
        </div>
      </motion.div>

      {thread.posts.map((p, i) => <PostCard key={p.post_ulid} post={p} onChanged={load} index={i} />)}

      <Composer threadUlid={thread.thread_ulid} onPosted={load} />
    </div>
  )
}
