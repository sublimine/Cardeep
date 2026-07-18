// web/src/pages/CommunityProfile.tsx — 08-forum-community F5: "/community/user/:handle"
// (carta §6.4). rep con desglose por origen recomputable a la vista — servido en vivo
// desde SUM(reputation_event.delta), nunca cacheado (servidor: services/api/routers/
// forum.py::user_profile).
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Award, MessageSquare, Search as SearchIcon } from 'lucide-react'
import Card from '../components/Card'
import EmptyState from '../components/EmptyState'
import { PageSkeleton } from '../components/LoadingSpinner'
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

  return (
    <div className="mx-auto p-[20px_24px_48px]" style={{ maxWidth: 700 }}>
      <div className="mb-5 flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-full text-[16px] font-bold" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>
          {(profile.name || profile.user_ulid).slice(0, 2).toUpperCase()}
        </div>
        <div>
          <div className="text-[16px] font-bold" style={{ color: 'var(--text-primary)' }}>{profile.name || 'Usuario'}</div>
          <div className="text-[11.5px] capitalize" style={{ color: 'var(--text-muted)' }}>{profile.role} · miembro desde {new Date(profile.member_since).toLocaleDateString('es-ES')}</div>
        </div>
      </div>

      <div className="mb-5 grid grid-cols-3 gap-3">
        <Card className="!p-4 text-center">
          <div className="text-[22px] font-extrabold" style={{ color: 'var(--text-primary)' }}>{profile.reputation}</div>
          <div className="text-[10.5px] uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>Reputación</div>
        </Card>
        <Card className="!p-4 text-center">
          <div className="text-[22px] font-extrabold" style={{ color: 'var(--text-primary)' }}>{profile.thread_count + profile.post_count}</div>
          <div className="text-[10.5px] uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>Aportaciones</div>
        </Card>
        <Card className="!p-4 text-center">
          <div className="text-[22px] font-extrabold" style={{ color: 'var(--text-primary)' }}>{profile.wanted_count}</div>
          <div className="text-[10.5px] uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>Búsquedas</div>
        </Card>
      </div>

      <Card>
        <h2 className="mb-3 flex items-center gap-1.5 text-[13px] font-bold" style={{ color: 'var(--text-primary)' }}>
          <Award className="h-4 w-4" /> Desglose de reputación
        </h2>
        {profile.reputation_breakdown.length === 0 ? (
          <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>Sin actividad de reputación todavía.</p>
        ) : (
          <div className="space-y-1.5">
            {profile.reputation_breakdown.map((b) => (
              <div key={b.reason} className="flex items-center justify-between text-[12.5px]">
                <span style={{ color: 'var(--text-secondary)' }}>{REASON_LABEL[b.reason] ?? b.reason} ({b.count})</span>
                <span className="font-semibold" style={{ color: b.total >= 0 ? '#10b981' : '#ef4444' }}>
                  {b.total >= 0 ? '+' : ''}{b.total}
                </span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
