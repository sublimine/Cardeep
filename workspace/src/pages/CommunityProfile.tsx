// web/src/pages/CommunityProfile.tsx — 08-forum-community F5: "/community/user/:handle"
// (carta §6.4). rep con desglose por origen recomputable a la vista — servido en vivo
// desde SUM(reputation_event.delta), nunca cacheado (servidor: services/api/routers/
// forum.py::user_profile).
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Award } from 'lucide-react'
import Card from '../components/Card'
import EmptyState from '../components/EmptyState'
import { PageSkeleton } from '../components/LoadingSpinner'
import Avatar from '../components/Avatar'
import CountUp from '../components/landing/CountUp'
import { forumApi, type UserProfile } from '../api/forum'

const REASON_LABEL: Record<string, string> = {
  upvote_anchor: 'Votos a favor con dato verificado',
  upvote_no_anchor: 'Votos a favor sin dato',
  wanted_closed_bought: 'Búsquedas cerradas (comprado vía Cardeep)',
  downvote_received: 'Votos en contra recibidos',
  downvote_cast: 'Votos en contra emitidos',
  staff_grant: 'Ajuste manual de staff',
}

export default function CommunityProfile() {
  const { id } = useParams<{ id: string }>()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    forumApi.profile(id).then((r) => setProfile(r.data)).catch(() => setProfile(null)).finally(() => setLoading(false))
  }, [id])

  if (loading) return <PageSkeleton />
  if (!profile) {
    return <div style={{ padding: '24px 28px' }}><EmptyState title="Usuario no encontrado" /></div>
  }

  const stats = [
    { label: 'Reputación', value: profile.reputation },
    { label: 'Aportaciones', value: profile.thread_count + profile.post_count },
    { label: 'Búsquedas', value: profile.wanted_count },
  ]

  return (
    <div className="mx-auto p-[20px_24px_48px]" style={{ maxWidth: 700 }}>
      <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="mb-5 flex items-center gap-3">
        <Avatar name={profile.name || profile.user_ulid} size="lg" />
        <div>
          <div className="text-[16px] font-bold" style={{ color: 'var(--text-primary)' }}>{profile.name || 'Usuario'}</div>
          <div className="text-[11.5px] capitalize" style={{ color: 'var(--text-muted)' }}>{profile.role} · miembro desde {new Date(profile.member_since).toLocaleDateString('es-ES')}</div>
        </div>
      </motion.div>

      <div className="mb-5 grid grid-cols-3 gap-3">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: i * 0.06, ease: [0.16, 1, 0.3, 1] }}
          >
            <Card className="!p-4 text-center">
              <div className="font-mono text-[22px] font-extrabold tabular-nums" style={{ color: 'var(--text-primary)' }}>
                <CountUp value={s.value} />
              </div>
              <div className="text-[10.5px] uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>{s.label}</div>
            </Card>
          </motion.div>
        ))}
      </div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}>
        <Card>
          <h2 className="mb-3 flex items-center gap-1.5 text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>
            <Award className="h-4 w-4" style={{ color: 'var(--c-brand)' }} /> Desglose de reputación
          </h2>
          {profile.reputation_breakdown.length === 0 ? (
            <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>Sin actividad de reputación todavía.</p>
          ) : (
            <div className="space-y-1">
              {profile.reputation_breakdown.map((b, i) => (
                <motion.div
                  key={b.reason}
                  initial={{ opacity: 0, x: -6 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2, delay: i * 0.04 }}
                  className="-mx-2 flex items-center justify-between rounded-md px-2 py-1.5 text-[12.5px] transition-colors hover:bg-[var(--bg-hover)]"
                >
                  <span style={{ color: 'var(--text-secondary)' }}>{REASON_LABEL[b.reason] ?? b.reason} <span className="tabular-nums">({b.count})</span></span>
                  <span className="font-mono font-semibold tabular-nums" style={{ color: b.total >= 0 ? 'var(--c-emerald)' : 'var(--c-rose)' }}>
                    {b.total >= 0 ? '+' : ''}{b.total}
                  </span>
                </motion.div>
              ))}
            </div>
          )}
        </Card>
      </motion.div>
    </div>
  )
}
