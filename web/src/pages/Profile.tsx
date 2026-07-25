import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MapPin, Briefcase, Calendar, Mail, Phone,
  TrendingUp, Car, Clock, Star, Edit3, Check, X,
} from 'lucide-react'
import Card from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import Avatar from '../components/Avatar'
import Timeline from '../components/Timeline'
import { useAuthContext } from '../auth/AuthContext'
import { useToast } from '../components/Toast'
import { cn } from '../lib/cn'
import type { TimelineItem } from '../components/Timeline'

// ── Mock data ─────────────────────────────────────────────────────────────────
// Icon accent is uniform brand blue for all four tiles — one brand hue drives
// structure everywhere; distinct hues are reserved for real status/trend
// meaning (see lib/theme.ts), not decorative per-metric coloring.

interface StatItem {
  label: string
  value: string
  icon: React.ElementType
}

const STATS: StatItem[] = [
  { label: 'Operaciones cerradas',    value: '47',   icon: TrendingUp },
  { label: 'Vehículos gestionados',   value: '270',  icon: Car        },
  { label: 'Tiempo de respuesta avg', value: '2.4h', icon: Clock      },
  { label: 'Valoración compradores',  value: '4.8★', icon: Star       },
]

const ACTIVITY: TimelineItem[] = [
  { id: 'a1', date: '30 Jun 2026 · 10:15', title: 'Oferta enviada — Audi A4 Avant, €26.500',      subtitle: 'Cliente: Johannes M.',         accent: 'blue'   },
  { id: 'a2', date: '30 Jun 2026 · 09:42', title: 'Prueba de conducción confirmada — VW Tiguan',   subtitle: 'Cita a las 14:30',             accent: 'green'  },
  { id: 'a3', date: '29 Jun 2026 · 16:55', title: 'Nota añadida al expediente BMW 320d',            subtitle: 'Cliente quiere interior negro', accent: 'gray'   },
  { id: 'a4', date: '29 Jun 2026 · 14:30', title: 'Recordatorio de seguimiento creado',             subtitle: 'Mercedes C220d · Peter K.',    accent: 'yellow' },
  { id: 'a5', date: '28 Jun 2026 · 11:10', title: 'Operación cerrada — BMW 320d xDrive, €23.400',  subtitle: 'Beneficio neto: €2.100',       accent: 'green'  },
]

// ── ProfileHero ───────────────────────────────────────────────────────────────

interface HeroProps {
  editing: boolean
  onEdit: () => void
  onSave: () => void
  onCancel: () => void
}

function ProfileHero({ editing, onEdit, onSave, onCancel }: HeroProps) {
  const { user } = useAuthContext()

  return (
    <Card padding={false} className="overflow-hidden">
      {/* Accent band */}
      <div className="h-20 bg-gradient-to-r from-accent-blue/15 via-accent-blue/25 to-accent-blue/10" />

      <div className="px-6 pb-6">
        {/* Avatar row */}
        <div className="flex items-end justify-between -mt-10 mb-4">
          <Avatar
            name={user?.name ?? 'Demo User'}
            size="lg"
            status="online"
            className="ring-4 ring-bg-surface shadow-elevation-2"
          />
          <div className="flex items-center gap-2 mb-1 min-h-[32px]">
            <AnimatePresence mode="wait" initial={false}>
              {editing ? (
                <motion.div
                  key="editing"
                  initial={{ opacity: 0, scale: 0.96 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.96 }}
                  transition={{ duration: 0.15, ease: 'easeOut' }}
                  className="flex items-center gap-2"
                >
                  <Button variant="ghost" size="sm" onClick={onCancel} icon={<X className="w-3.5 h-3.5" />}>
                    Cancelar
                  </Button>
                  <Button size="sm" onClick={onSave} icon={<Check className="w-3.5 h-3.5" />}>
                    Guardar
                  </Button>
                </motion.div>
              ) : (
                <motion.div
                  key="view"
                  initial={{ opacity: 0, scale: 0.96 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.96 }}
                  transition={{ duration: 0.15, ease: 'easeOut' }}
                >
                  <Button variant="secondary" size="sm" onClick={onEdit} icon={<Edit3 className="w-3.5 h-3.5" />}>
                    Editar perfil
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Identity */}
        <h2 className="text-xl font-bold text-text-primary">{user?.name ?? 'Demo User'}</h2>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2">
          <span className="flex items-center gap-1.5 text-sm text-text-secondary">
            <Briefcase className="w-3.5 h-3.5 shrink-0" />
            {user?.role === 'admin' ? 'Administrador' : 'Agente de ventas'}
          </span>
          <span className="text-border-subtle select-none">·</span>
          <span className="flex items-center gap-1.5 text-sm text-text-secondary">
            <MapPin className="w-3.5 h-3.5 shrink-0" />
            Garage Müller GmbH · Madrid, ES
          </span>
          <span className="text-border-subtle select-none">·</span>
          <span className="flex items-center gap-1.5 text-sm text-text-muted">
            <Calendar className="w-3.5 h-3.5 shrink-0" />
            Miembro desde Ene 2024
          </span>
        </div>
      </div>
    </Card>
  )
}

// ── Stats row ─────────────────────────────────────────────────────────────────

function StatsRow() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {STATS.map((stat, i) => {
        const Icon = stat.icon
        return (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08 + i * 0.06, duration: 0.32, ease: 'easeOut' }}
          >
            <Card hover className="flex flex-col gap-3">
              <div className="w-8 h-8 rounded-lg bg-accent-blue/10 flex items-center justify-center shrink-0">
                <Icon className="w-4 h-4 text-accent-blue" />
              </div>
              <div>
                <p className="text-lg font-bold text-text-primary tabular-nums leading-none">{stat.value}</p>
                <p className="text-xs text-text-muted mt-1 leading-snug">{stat.label}</p>
              </div>
            </Card>
          </motion.div>
        )
      })}
    </div>
  )
}

// ── Edit form ─────────────────────────────────────────────────────────────────

function EditForm({ editing }: { editing: boolean }) {
  const { user } = useAuthContext()
  const [name,     setName]     = useState(user?.name  ?? '')
  const [email,    setEmail]    = useState(user?.email ?? '')
  const [phone,    setPhone]    = useState('+34 612 345 678')
  const [location, setLocation] = useState('Madrid, España')
  const [bio,      setBio]      = useState('Especialista en vehículos premium de importación. Más de 8 años en el sector. Enfocado en proporcionar la mejor experiencia de compra a compradores particulares y flotas.')

  return (
    <Card>
      <h3 className="text-sm font-semibold text-text-primary mb-5">Información de contacto</h3>
      <div className="space-y-4">
        <Input
          label="Nombre completo"
          value={name}
          onChange={e => setName(e.target.value)}
          disabled={!editing}
        />
        <Input
          label="Email profesional"
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          disabled={!editing}
          icon={<Mail className="w-4 h-4" />}
        />
        <Input
          label="Teléfono"
          type="tel"
          value={phone}
          onChange={e => setPhone(e.target.value)}
          disabled={!editing}
          icon={<Phone className="w-4 h-4" />}
        />
        <Input
          label="Ubicación"
          value={location}
          onChange={e => setLocation(e.target.value)}
          disabled={!editing}
          icon={<MapPin className="w-4 h-4" />}
        />
        <div>
          <label className="block text-xs font-medium text-text-secondary mb-1.5 uppercase tracking-wide">
            Biografía
          </label>
          <textarea
            value={bio}
            onChange={e => setBio(e.target.value)}
            disabled={!editing}
            rows={4}
            className={cn(
              'w-full px-3.5 py-2.5 rounded-md text-sm text-text-primary placeholder:text-text-muted',
              'bg-glass-subtle border border-border-subtle resize-none',
              'focus:outline-none focus:ring-2 focus:ring-accent-blue/30 focus:border-border-active',
              'disabled:opacity-40 disabled:cursor-not-allowed',
              'transition-all duration-200',
            )}
          />
        </div>
      </div>
    </Card>
  )
}

// ── Activity panel ────────────────────────────────────────────────────────────

function ActivityPanel() {
  return (
    <Card>
      <h3 className="text-sm font-semibold text-text-primary mb-5">Actividad reciente</h3>
      <Timeline items={ACTIVITY} />
    </Card>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Profile() {
  const { success } = useToast()
  const [editing, setEditing] = useState(false)

  function handleSave() {
    setEditing(false)
    success('Perfil actualizado correctamente')
  }

  return (
    <div className="p-4 md:p-6 max-w-5xl mx-auto space-y-5">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
      >
        <h1 className="text-xl font-bold text-text-primary">Mi perfil</h1>
        <p className="text-sm text-text-muted mt-0.5">Información pública de tu cuenta</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.06, duration: 0.35, ease: 'easeOut' }}
      >
        <ProfileHero
          editing={editing}
          onEdit={() => setEditing(true)}
          onSave={handleSave}
          onCancel={() => setEditing(false)}
        />
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.12, duration: 0.35, ease: 'easeOut' }}
      >
        <StatsRow />
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.18, duration: 0.35, ease: 'easeOut' }}
        className="grid grid-cols-1 lg:grid-cols-5 gap-5"
      >
        <div className="lg:col-span-3">
          <EditForm editing={editing} />
        </div>
        <div className="lg:col-span-2">
          <ActivityPanel />
        </div>
      </motion.div>
    </div>
  )
}
