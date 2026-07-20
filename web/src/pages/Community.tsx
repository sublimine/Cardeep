// web/src/pages/Community.tsx — 08-forum-community F5: the forum feed
// (carta §6.2). Opens only in F5, behind masa-critica per the carta's own ordering
// (§3/§9) — but now that it exists, it is real data end-to-end, zero mocks.
import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { MessageSquare, TrendingUp, Clock, MapPin, Plus, ShieldCheck, ChevronRight } from 'lucide-react'
import Card from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import Select from '../components/Select'
import Modal from '../components/Modal'
import EmptyState from '../components/EmptyState'
import { Badge } from '../components/Badge'
import { PageSkeleton } from '../components/LoadingSpinner'
import { useToast } from '../components/Toast'
import { ApiError } from '../api/client'
import { forumApi, type ThreadSummary, type ThreadType, type AnchorInput } from '../api/forum'
import { wantedApi, type Pulse, type ProvinceOption } from '../api/wanted'
import { DataLinker } from '../components/forum/DataLinker'
import CountUp from '../components/landing/CountUp'

const ENTRANCE = { duration: 0.35, ease: [0.16, 1, 0.3, 1] as const }

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

function timeAgo(iso: string): string {
  const h = (Date.now() - new Date(iso).getTime()) / 3_600_000
  if (h < 1) return 'hace unos minutos'
  if (h < 24) return `hace ${Math.round(h)} h`
  return `hace ${Math.round(h / 24)} d`
}

// ---------------------------------------------------------------------------
// Province activity — magnitude encoded as bar length (not color), the
// perceptually accurate encoding for a ranked list. Real counts derived from
// the threads already loaded on this page, no separate endpoint.
// ---------------------------------------------------------------------------

function ProvinceActivity({ provinces }: { provinces: { code: string; activeThreads: number }[] }) {
  const top = [...provinces].sort((a, b) => b.activeThreads - a.activeThreads).slice(0, 6)
  if (top.length === 0) return null
  const max = Math.max(...top.map((p) => p.activeThreads))

  return (
    <div className="flex flex-wrap gap-2">
      {top.map((p, i) => {
        const pct = max > 0 ? Math.round((p.activeThreads / max) * 100) : 0
        return (
          <motion.div
            key={p.code}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, delay: i * 0.05 }}
            className="relative overflow-hidden rounded-full px-3 py-1.5 text-[11px]"
            style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
            title={`${p.activeThreads} hilo${p.activeThreads === 1 ? '' : 's'} activo${p.activeThreads === 1 ? '' : 's'} en ${p.code}`}
          >
            <span
              aria-hidden
              className="absolute inset-y-0 left-0 rounded-full"
              style={{ width: `${pct}%`, background: 'var(--c-brand)', opacity: 0.14 }}
            />
            <span className="relative inline-flex items-center gap-1.5" style={{ color: 'var(--text-secondary)' }}>
              <MapPin className="h-3 w-3" /> {p.code} ·{' '}
              <span className="font-mono font-semibold tabular-nums" style={{ color: 'var(--text-primary)' }}>{p.activeThreads}</span>
            </span>
          </motion.div>
        )
      })}
    </div>
  )
}

function PulseHero({ pulse, provinces }: { pulse: Pulse | null; provinces: { code: string; activeThreads: number }[] }) {
  const cards = [
    { label: 'Hilos activos (24h)', value: pulse?.threads_active_24h ?? null },
    { label: 'Peticiones abiertas', value: pulse?.wanted_open ?? null },
    { label: 'Coincidencias (7d)', value: pulse?.matches_served_7d ?? null },
  ]

  return (
    <div className="mb-6">
      <div className="mb-3 grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))' }}>
        {cards.map((c, i) => (
          <motion.div
            key={c.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...ENTRANCE, delay: i * 0.06 }}
          >
            <Card className="!p-4">
              <div className="text-[11px] uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>{c.label}</div>
              <div className="mt-1 font-mono text-[26px] font-extrabold tabular-nums" style={{ color: 'var(--text-primary)' }}>
                {c.value != null ? <CountUp value={c.value} /> : '—'}
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
      {/* Heatmap simplificado: barras de magnitud por provincia, no mapa SVG interactivo —
          decisión de alcance declarada (el primitivo SpainMap real, CoverageMap.tsx, existe
          pero sirve absorción de demanda de mercado, un dato distinto de la actividad del
          foro; reutilizarlo aquí mezclaría dos series). Misma fuente de datos (threads ya
          cargados) que un heatmap real usaría, con la longitud de barra codificando magnitud —
          más preciso perceptualmente que un degradado de color para una lista de 6 elementos. */}
      <ProvinceActivity provinces={provinces} />
    </div>
  )
}

function NewThreadModal({ open, onClose, provinces, onCreated }: {
  open: boolean
  onClose: () => void
  provinces: ProvinceOption[]
  onCreated: (t: ThreadSummary) => void
}) {
  const { error: toastErr, success } = useToast()
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [threadType, setThreadType] = useState<ThreadType>('discussion')
  const [province, setProvince] = useState('')
  const [anchors, setAnchors] = useState<AnchorInput[]>([])
  const [submitting, setSubmitting] = useState(false)

  const submit = useCallback(async () => {
    if (!title.trim() || !body.trim()) {
      toastErr('Título y contenido son obligatorios')
      return
    }
    if (threadType === 'price_check' && anchors.length === 0) {
      toastErr('Los hilos "¿Es buen precio?" necesitan un dato anclado — vincúlalo abajo')
      return
    }
    setSubmitting(true)
    try {
      const { data } = await forumApi.createThread({
        title: title.trim(), body: body.trim(), thread_type: threadType,
        province_code: province || null, anchors,
      })
      success('Hilo publicado')
      onCreated(data)
      setTitle(''); setBody(''); setThreadType('discussion'); setProvince(''); setAnchors([])
      onClose()
    } catch (err) {
      toastErr(errorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }, [title, body, threadType, province, anchors, success, toastErr, onCreated, onClose])

  return (
    <Modal open={open} onClose={onClose} title="Nuevo hilo" size="lg">
      <div className="space-y-3">
        <Input label="Título" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="¿Por qué caen los precios de eléctricos en Barcelona?" />
        <textarea
          className="w-full rounded-md p-3 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-accent-blue/30"
          style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', color: 'var(--text-primary)' }}
          rows={4}
          placeholder="Contenido del hilo…"
          value={body}
          onChange={(e) => setBody(e.target.value)}
        />
        <div className="grid grid-cols-2 gap-3">
          <Select
            label="Tipo"
            options={[{ value: 'discussion', label: 'Conversación' }, { value: 'price_check', label: '¿Es buen precio?' }]}
            value={threadType}
            onChange={(e) => setThreadType(e.target.value as ThreadType)}
          />
          <Select
            label="Provincia (opcional)"
            placeholder="Sin provincia"
            options={provinces.map((p) => ({ value: p.code, label: p.name }))}
            value={province}
            onChange={(e) => setProvince(e.target.value)}
          />
        </div>
        {threadType === 'price_check' && (
          <div>
            <p className="mb-1.5 text-[11px]" style={{ color: 'var(--text-muted)' }}>
              Los hilos "¿Es buen precio?" necesitan un dato anclado (vehículo real) — obligatorio.
            </p>
            <DataLinker onSelect={(a) => setAnchors([a])} label={anchors.length > 0 ? `Vinculado: ${anchors[0].anchor_ref.slice(0, 12)}…` : 'Vincular dato'} />
          </div>
        )}
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>Cancelar</Button>
          <Button onClick={submit} loading={submitting}>Publicar hilo</Button>
        </div>
      </div>
    </Modal>
  )
}

function ThreadRow({ thread, index = 0 }: { thread: ThreadSummary; index?: number }) {
  const navigate = useNavigate()
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: Math.min(index, 10) * 0.04 }}
    >
      <Card className="group mb-2 cursor-pointer" onClick={() => navigate(`/community/thread/${thread.thread_ulid}`)} hover>
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-[13.5px] font-semibold" style={{ color: 'var(--text-primary)' }}>{thread.title}</span>
              {thread.thread_type === 'price_check' && <Badge color="blue">¿Buen precio?</Badge>}
              {thread.verified_anchor_count > 0 && (
                <span className="inline-flex items-center gap-1 text-[10.5px]" style={{ color: 'var(--c-emerald)' }}>
                  <ShieldCheck className="h-3 w-3" /> {thread.verified_anchor_count} dato{thread.verified_anchor_count > 1 ? 's' : ''}
                </span>
              )}
            </div>
            <div className="mt-1 flex items-center gap-3 text-[11px] tabular-nums" style={{ color: 'var(--text-muted)' }}>
              <span className="inline-flex items-center gap-1"><MessageSquare className="h-3 w-3" /> {thread.reply_count}</span>
              <span className="inline-flex items-center gap-1"><TrendingUp className="h-3 w-3" /> {thread.net_votes}</span>
              {thread.province_code && <span className="inline-flex items-center gap-1"><MapPin className="h-3 w-3" /> {thread.province_code}</span>}
              <span className="inline-flex items-center gap-1"><Clock className="h-3 w-3" /> {timeAgo(thread.last_reply_at)}</span>
              {/* carta §4.7: el rol del autor se muestra SIEMPRE */}
              {thread.author_role && <Badge color={thread.author_role === 'dealer' ? 'blue' : thread.author_role === 'staff' ? 'purple' : 'gray'}>{thread.author_role}</Badge>}
            </div>
          </div>
          <ChevronRight
            className="mt-0.5 h-4 w-4 shrink-0 opacity-0 transition-all duration-200 group-hover:translate-x-0.5 group-hover:opacity-100"
            style={{ color: 'var(--text-muted)' }}
          />
        </div>
      </Card>
    </motion.div>
  )
}

export default function Community() {
  const [loading, setLoading] = useState(true)
  const [threads, setThreads] = useState<ThreadSummary[]>([])
  const [sort, setSort] = useState<'hot' | 'recent'>('hot')
  const [pulse, setPulse] = useState<Pulse | null>(null)
  const [provinces, setProvinces] = useState<ProvinceOption[]>([])
  const [modalOpen, setModalOpen] = useState(false)

  const load = useCallback(async () => {
    const [t, p] = await Promise.all([
      forumApi.threads({ sort }).then((r) => r.data).catch(() => []),
      wantedApi.pulse().then((r) => r.data).catch(() => null),
    ])
    setThreads(t)
    setPulse(p)
  }, [sort])

  useEffect(() => {
    wantedApi.provinces().then((r) => setProvinces(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    load().finally(() => setLoading(false))
  }, [load])

  const activityByProvince = threads.reduce<Record<string, number>>((acc, t) => {
    if (t.province_code) acc[t.province_code] = (acc[t.province_code] ?? 0) + 1
    return acc
  }, {})

  if (loading) return <PageSkeleton />

  return (
    <div className="mx-auto p-[20px_24px_48px]" style={{ maxWidth: 900 }}>
      <motion.div
        initial={{ opacity: 0, y: -6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="mb-5 flex items-start justify-between gap-3"
      >
        <div>
          <h1 className="mb-1 text-[20px] font-bold" style={{ color: 'var(--text-primary)' }}>Foro</h1>
          <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
            Conversación anclada a dato real de mercado — vehículo, dealer o provincia.
          </p>
        </div>
        <Button onClick={() => setModalOpen(true)} icon={<Plus className="h-4 w-4" />}>Nuevo hilo</Button>
      </motion.div>

      <PulseHero
        pulse={pulse}
        provinces={Object.entries(activityByProvince).map(([code, activeThreads]) => ({ code, activeThreads }))}
      />

      <div className="mb-3 flex gap-2">
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={() => setSort('hot')}
          className="rounded-md px-3 py-1.5 text-[12px] font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
          style={{
            background: sort === 'hot' ? 'var(--bg-surface)' : 'transparent',
            color: sort === 'hot' ? 'var(--text-primary)' : 'var(--text-secondary)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          Destacados
        </motion.button>
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={() => setSort('recent')}
          className="rounded-md px-3 py-1.5 text-[12px] font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
          style={{
            background: sort === 'recent' ? 'var(--bg-surface)' : 'transparent',
            color: sort === 'recent' ? 'var(--text-primary)' : 'var(--text-secondary)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          Recientes
        </motion.button>
      </div>

      {threads.length === 0 ? (
        <EmptyState
          icon={<MessageSquare className="h-6 w-6" />}
          title="Sin hilos todavía"
          message="Sé el primero en abrir una conversación anclada a dato real."
          action={<Button onClick={() => setModalOpen(true)}>Nuevo hilo</Button>}
        />
      ) : (
        <div>
          {threads.map((t, i) => <ThreadRow key={t.thread_ulid} thread={t} index={i} />)}
        </div>
      )}

      <NewThreadModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        provinces={provinces}
        onCreated={() => void load()}
      />
    </div>
  )
}
