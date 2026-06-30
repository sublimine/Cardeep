import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Settings2, Bell, Shield, Users, CreditCard,
  Monitor, Smartphone, Plus, Download,
} from 'lucide-react'
import Card from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import Select from '../components/Select'
import { Switch } from '../components/Switch'
import { Badge } from '../components/Badge'
import Avatar from '../components/Avatar'
import { useToast } from '../components/Toast'
import { useAuthContext } from '../auth/AuthContext'
import { cn } from '../lib/cn'

// ── Types ─────────────────────────────────────────────────────────────────────

type Tab = 'general' | 'notificaciones' | 'seguridad' | 'equipo' | 'facturacion'

interface NotifState {
  emailInquiries: boolean
  emailOffers: boolean
  emailStale: boolean
  emailWeekly: boolean
  appRealtime: boolean
  appTeam: boolean
  appReminders: boolean
  pushEnabled: boolean
  pushUrgent: boolean
}

interface Session {
  id: string
  browser: string
  os: string
  location: string
  lastActive: string
  current: boolean
}

interface Member {
  id: string
  name: string
  email: string
  role: 'Admin' | 'Agente' | 'Viewer'
  status: 'active' | 'pending'
}

interface Invoice {
  id: string
  date: string
  description: string
  amount: number
  status: 'paid' | 'pending' | 'failed'
}

// ── Mock data ─────────────────────────────────────────────────────────────────

const SESSIONS: Session[] = [
  { id: 's1', browser: 'Chrome 125',  os: 'macOS 14',   location: 'Madrid, ES',   lastActive: 'Ahora',   current: true  },
  { id: 's2', browser: 'Safari 17',   os: 'iPhone 15',  location: 'Madrid, ES',   lastActive: 'Hace 2h', current: false },
  { id: 's3', browser: 'Firefox 126', os: 'Windows 11', location: 'Valencia, ES', lastActive: 'Hace 3d', current: false },
]

const MEMBERS: Member[] = [
  { id: 'm1', name: 'Carlos García',  email: 'carlos@garage.es', role: 'Admin',  status: 'active'  },
  { id: 'm2', name: 'Ana Martínez',   email: 'ana@garage.es',    role: 'Agente', status: 'active'  },
  { id: 'm3', name: 'Pedro López',    email: 'pedro@garage.es',  role: 'Agente', status: 'active'  },
  { id: 'm4', name: 'María Sánchez',  email: 'maria@garage.es',  role: 'Viewer', status: 'pending' },
]

const INVOICES: Invoice[] = [
  { id: 'inv-001', date: '01 Jun 2026', description: 'Plan Professional — Jun 2026', amount: 99, status: 'paid'    },
  { id: 'inv-002', date: '01 May 2026', description: 'Plan Professional — May 2026', amount: 99, status: 'paid'    },
  { id: 'inv-003', date: '01 Abr 2026', description: 'Plan Professional — Abr 2026', amount: 99, status: 'paid'    },
]

const INVOICE_STATUS: Record<Invoice['status'], { color: 'green' | 'yellow' | 'red'; label: string }> = {
  paid:    { color: 'green',  label: 'Pagada'    },
  pending: { color: 'yellow', label: 'Pendiente' },
  failed:  { color: 'red',    label: 'Fallida'   },
}

// ── Tab config ────────────────────────────────────────────────────────────────

const TABS: { id: Tab; label: string; icon: React.ElementType }[] = [
  { id: 'general',        label: 'General',        icon: Settings2  },
  { id: 'notificaciones', label: 'Notificaciones', icon: Bell       },
  { id: 'seguridad',      label: 'Seguridad',      icon: Shield     },
  { id: 'equipo',         label: 'Equipo',         icon: Users      },
  { id: 'facturacion',    label: 'Facturación',    icon: CreditCard },
]

// ── Shared ────────────────────────────────────────────────────────────────────

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">
      {children}
    </h3>
  )
}

function SectionCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="p-4 rounded-lg border border-border-subtle bg-bg-surface space-y-4">
      {children}
    </div>
  )
}

// ── General tab ───────────────────────────────────────────────────────────────

function GeneralTab() {
  const { user } = useAuthContext()
  const { success } = useToast()
  const [name,     setName]     = useState(user?.name  ?? '')
  const [email,    setEmail]    = useState(user?.email ?? '')
  const [phone,    setPhone]    = useState('+34 612 345 678')
  const [company,  setCompany]  = useState('Garage Müller GmbH')
  const [vat,      setVat]      = useState('ES-B12345678')
  const [country,  setCountry]  = useState('ES')
  const [language, setLanguage] = useState('es')
  const [timezone, setTimezone] = useState('Europe/Madrid')

  return (
    <div className="space-y-8 max-w-lg">
      <div>
        <SectionTitle>Información personal</SectionTitle>
        <SectionCard>
          <Input label="Nombre completo" value={name}  onChange={e => setName(e.target.value)}  />
          <Input label="Email"           value={email} onChange={e => setEmail(e.target.value)} type="email" />
          <Input label="Teléfono"        value={phone} onChange={e => setPhone(e.target.value)} type="tel" />
        </SectionCard>
      </div>

      <div>
        <SectionTitle>Empresa</SectionTitle>
        <SectionCard>
          <Input label="Nombre empresa" value={company} onChange={e => setCompany(e.target.value)} />
          <Input label="NIF / VAT"       value={vat}    onChange={e => setVat(e.target.value)} />
          <Select
            label="País"
            value={country}
            onChange={e => setCountry(e.target.value)}
            options={[
              { value: 'ES', label: 'España'       },
              { value: 'DE', label: 'Alemania'     },
              { value: 'FR', label: 'Francia'      },
              { value: 'IT', label: 'Italia'       },
              { value: 'NL', label: 'Países Bajos' },
              { value: 'PT', label: 'Portugal'     },
            ]}
          />
        </SectionCard>
      </div>

      <div>
        <SectionTitle>Preferencias</SectionTitle>
        <SectionCard>
          <Select
            label="Idioma"
            value={language}
            onChange={e => setLanguage(e.target.value)}
            options={[
              { value: 'es', label: 'Español'  },
              { value: 'en', label: 'English'  },
              { value: 'de', label: 'Deutsch'  },
              { value: 'fr', label: 'Français' },
            ]}
          />
          <Select
            label="Zona horaria"
            value={timezone}
            onChange={e => setTimezone(e.target.value)}
            options={[
              { value: 'Europe/Madrid', label: 'Europa/Madrid (UTC+2)'  },
              { value: 'Europe/Berlin', label: 'Europa/Berlín (UTC+2)'  },
              { value: 'Europe/Paris',  label: 'Europa/París (UTC+2)'   },
              { value: 'Europe/London', label: 'Europa/Londres (UTC+1)' },
            ]}
          />
        </SectionCard>
      </div>

      <Button onClick={() => success('Configuración guardada')}>Guardar cambios</Button>
    </div>
  )
}

// ── Notificaciones tab ────────────────────────────────────────────────────────

function NotificacionesTab() {
  const { success } = useToast()
  const [n, setN] = useState<NotifState>({
    emailInquiries: true,
    emailOffers:    true,
    emailStale:     false,
    emailWeekly:    true,
    appRealtime:    true,
    appTeam:        true,
    appReminders:   true,
    pushEnabled:    false,
    pushUrgent:     false,
  })

  function toggle(key: keyof NotifState) {
    setN(prev => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <div className="space-y-8 max-w-lg">
      <div>
        <SectionTitle>Email</SectionTitle>
        <SectionCard>
          <Switch checked={n.emailInquiries} onCheckedChange={() => toggle('emailInquiries')} label="Nuevas consultas"        description="Email al recibir una nueva consulta de un comprador" />
          <Switch checked={n.emailOffers}    onCheckedChange={() => toggle('emailOffers')}    label="Actualizaciones de oferta" description="Cambios de estado en ofertas enviadas" />
          <Switch checked={n.emailStale}     onCheckedChange={() => toggle('emailStale')}     label="Alertas de stock parado"  description="Vehículos con más de 60 días en stock" />
          <Switch checked={n.emailWeekly}    onCheckedChange={() => toggle('emailWeekly')}    label="Resumen semanal"          description="KPIs y métricas clave cada lunes por la mañana" />
        </SectionCard>
      </div>

      <div>
        <SectionTitle>In-app</SectionTitle>
        <SectionCard>
          <Switch checked={n.appRealtime}  onCheckedChange={() => toggle('appRealtime')}  label="Tiempo real"          description="Notificaciones instantáneas en el panel lateral" />
          <Switch checked={n.appTeam}      onCheckedChange={() => toggle('appTeam')}      label="Actividad del equipo" description="Cuando un compañero actualiza un trato o vehículo" />
          <Switch checked={n.appReminders} onCheckedChange={() => toggle('appReminders')} label="Recordatorios"        description="Seguimientos y citas próximas" />
        </SectionCard>
      </div>

      <div>
        <SectionTitle>Móvil (Push)</SectionTitle>
        <SectionCard>
          <Switch checked={n.pushEnabled} onCheckedChange={() => toggle('pushEnabled')} label="Push notifications" description="Activa las notificaciones push en tu dispositivo" />
          <Switch checked={n.pushUrgent}  onCheckedChange={() => toggle('pushUrgent')}  label="Solo urgencias"      description="Solo alertas críticas (requiere push activo)" disabled={!n.pushEnabled} />
        </SectionCard>
      </div>

      <Button onClick={() => success('Preferencias de notificación guardadas')}>Guardar preferencias</Button>
    </div>
  )
}

// ── Seguridad tab ─────────────────────────────────────────────────────────────

function SeguridadTab() {
  const { success } = useToast()
  const [pwd,      setPwd]      = useState({ current: '', next: '', confirm: '' })
  const [twoFa,    setTwoFa]    = useState(false)
  const [sessions, setSessions] = useState<Session[]>(SESSIONS)

  const pwdValid = pwd.current.length > 0 && pwd.next.length >= 8 && pwd.next === pwd.confirm

  function changePassword() {
    setPwd({ current: '', next: '', confirm: '' })
    success('Contraseña actualizada correctamente')
  }

  function revokeSession(id: string) {
    setSessions(s => s.filter(x => x.id !== id))
    success('Sesión revocada')
  }

  return (
    <div className="space-y-8 max-w-lg">
      <div>
        <SectionTitle>Cambiar contraseña</SectionTitle>
        <SectionCard>
          <Input label="Contraseña actual"   type="password" placeholder="••••••••" value={pwd.current}  onChange={e => setPwd(p => ({ ...p, current:  e.target.value }))} />
          <Input label="Nueva contraseña"    type="password" placeholder="••••••••" value={pwd.next}     onChange={e => setPwd(p => ({ ...p, next:     e.target.value }))} hint="Mínimo 8 caracteres" />
          <Input label="Confirmar contraseña" type="password" placeholder="••••••••" value={pwd.confirm}  onChange={e => setPwd(p => ({ ...p, confirm:  e.target.value }))} error={pwd.confirm && pwd.next !== pwd.confirm ? 'Las contraseñas no coinciden' : undefined} />
          <Button onClick={changePassword} disabled={!pwdValid}>Actualizar contraseña</Button>
        </SectionCard>
      </div>

      <div>
        <SectionTitle>Autenticación en dos pasos</SectionTitle>
        <div className="p-4 rounded-lg border border-border-subtle bg-bg-surface">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-text-primary">Autenticador TOTP</p>
              <p className="text-xs text-text-muted mt-0.5">Usa Google Authenticator, Authy u otra app compatible</p>
            </div>
            <Switch checked={twoFa} onCheckedChange={setTwoFa} />
          </div>
          {twoFa && (
            <p className="mt-3 text-xs text-text-secondary border-t border-border-subtle pt-3">
              2FA activado. Necesitarás tu código de verificación en cada inicio de sesión.
            </p>
          )}
        </div>
      </div>

      <div>
        <SectionTitle>Sesiones activas</SectionTitle>
        <div className="space-y-2">
          {sessions.map(sess => (
            <div key={sess.id} className="flex items-center gap-3 p-3 rounded-lg border border-border-subtle bg-bg-surface">
              <div className="w-8 h-8 rounded-md bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shrink-0">
                {sess.os.includes('iPhone') ? (
                  <Smartphone className="w-4 h-4 text-accent-blue" />
                ) : (
                  <Monitor className="w-4 h-4 text-accent-blue" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-text-primary">{sess.browser} · {sess.os}</p>
                <p className="text-xs text-text-muted mt-0.5">{sess.location} · {sess.lastActive}</p>
              </div>
              {sess.current ? (
                <Badge color="green" dot>Actual</Badge>
              ) : (
                <Button variant="ghost" size="sm" onClick={() => revokeSession(sess.id)} className="text-accent-rose hover:text-accent-rose shrink-0">
                  Revocar
                </Button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ── Equipo tab ────────────────────────────────────────────────────────────────

function EquipoTab() {
  const { success } = useToast()
  const [invite,  setInvite]  = useState({ email: '', role: 'Agente' })
  const [members, setMembers] = useState<Member[]>(MEMBERS)

  function sendInvite() {
    success(`Invitación enviada a ${invite.email}`)
    setInvite({ email: '', role: 'Agente' })
  }

  function removeMember(id: string) {
    setMembers(m => m.filter(x => x.id !== id))
    success('Miembro eliminado del equipo')
  }

  return (
    <div className="space-y-8 max-w-lg">
      <div>
        <SectionTitle>Invitar miembro</SectionTitle>
        <div className="grid grid-cols-[1fr_140px] items-end gap-3 mb-3">
          <Input
            label="Email"
            placeholder="correo@empresa.es"
            type="email"
            value={invite.email}
            onChange={e => setInvite(p => ({ ...p, email: e.target.value }))}
          />
          <Select
            label="Rol"
            value={invite.role}
            onChange={e => setInvite(p => ({ ...p, role: e.target.value }))}
            options={[
              { value: 'Admin',  label: 'Admin'  },
              { value: 'Agente', label: 'Agente' },
              { value: 'Viewer', label: 'Viewer' },
            ]}
          />
        </div>
        <Button
          icon={<Plus className="w-4 h-4" />}
          onClick={sendInvite}
          disabled={!invite.email.includes('@')}
        >
          Enviar invitación
        </Button>
      </div>

      <div>
        <SectionTitle>Miembros ({members.length})</SectionTitle>
        <div className="space-y-2">
          {members.map(m => (
            <div key={m.id} className="flex items-center gap-3 p-3 rounded-lg border border-border-subtle bg-bg-surface">
              <Avatar name={m.name} size="sm" status={m.status === 'active' ? 'online' : undefined} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-text-primary">{m.name}</p>
                <p className="text-xs text-text-muted truncate">{m.email}</p>
              </div>
              <Badge color={m.status === 'pending' ? 'yellow' : 'blue'}>{m.role}</Badge>
              {m.status === 'pending' && <Badge color="yellow" dot>Pendiente</Badge>}
              {m.role !== 'Admin' && (
                <button
                  onClick={() => removeMember(m.id)}
                  className="w-6 h-6 flex items-center justify-center rounded text-text-muted hover:text-accent-rose hover:bg-rose-500/10 transition-colors duration-150 shrink-0 text-base leading-none"
                  aria-label="Eliminar miembro"
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ── Facturación tab ───────────────────────────────────────────────────────────

function UsageBar({ label, used, max }: { label: string; used: number; max: number }) {
  const pct = Math.round((used / max) * 100)
  return (
    <div>
      <div className="flex justify-between text-xs mb-1.5">
        <span className="text-text-secondary">{label}</span>
        <span className="text-text-muted tabular-nums">{used} / {max}</span>
      </div>
      <div className="h-1.5 rounded-full bg-border-subtle overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.7, delay: 0.15, ease: [0.32, 0.72, 0, 1] }}
          className={cn('h-full rounded-full', pct >= 80 ? 'bg-accent-rose' : 'bg-accent-blue')}
        />
      </div>
    </div>
  )
}

function BillingTab() {
  const { success } = useToast()

  return (
    <div className="space-y-6 max-w-lg">
      {/* Plan */}
      <div>
        <SectionTitle>Plan actual</SectionTitle>
        <div className="p-4 rounded-lg border border-blue-500/30 bg-blue-500/5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="font-semibold text-text-primary">Professional</p>
              <p className="text-xs text-text-muted mt-0.5">Facturado anualmente · Renovación: 1 Jul 2026</p>
            </div>
            <div className="text-right shrink-0">
              <span className="text-2xl font-bold text-text-primary">€99</span>
              <span className="text-xs text-text-muted">/mes</span>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-blue-500/20 flex gap-3">
            <Button variant="ghost" size="sm" onClick={() => success('Contacta con ventas para cambiar de plan')}>Cambiar plan</Button>
            <Button variant="ghost" size="sm" className="text-accent-rose hover:text-accent-rose" onClick={() => success('Contacta con soporte para gestionar la cancelación')}>Cancelar</Button>
          </div>
        </div>
      </div>

      {/* Usage */}
      <div>
        <SectionTitle>Uso del plan</SectionTitle>
        <SectionCard>
          <UsageBar label="Vehículos en stock"     used={270} max={500} />
          <UsageBar label="Miembros del equipo"    used={4}   max={10}  />
          <UsageBar label="Integraciones activas"  used={1}   max={5}   />
        </SectionCard>
      </div>

      {/* Invoices */}
      <div>
        <SectionTitle>Facturas</SectionTitle>
        <div className="rounded-lg border border-border-subtle overflow-hidden">
          {INVOICES.map((inv, i) => {
            const { color, label } = INVOICE_STATUS[inv.status]
            return (
              <div
                key={inv.id}
                className={cn(
                  'flex items-center gap-3 px-4 py-3 bg-bg-surface hover:bg-bg-elevated transition-colors duration-150',
                  i < INVOICES.length - 1 && 'border-b border-border-subtle',
                )}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-text-primary">{inv.description}</p>
                  <p className="text-xs text-text-muted mt-0.5">{inv.date}</p>
                </div>
                <span className="text-sm font-semibold text-text-primary tabular-nums shrink-0">€{inv.amount}</span>
                <Badge color={color}>{label}</Badge>
                <button
                  className="text-text-muted hover:text-accent-blue transition-colors duration-150 p-1 rounded shrink-0"
                  aria-label="Descargar factura"
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>
            )
          })}
        </div>
      </div>

      {/* Payment method */}
      <div>
        <SectionTitle>Método de pago</SectionTitle>
        <div className="flex items-center gap-3 p-4 rounded-lg border border-border-subtle bg-bg-surface">
          <div className="w-10 h-7 rounded bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shrink-0">
            <CreditCard className="w-4 h-4 text-accent-blue" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-text-primary">Visa ···· 4242</p>
            <p className="text-xs text-text-muted">Vence 12/2027</p>
          </div>
          <Button variant="ghost" size="sm" onClick={() => success('Redirigiendo al portal de facturación…')}>Actualizar</Button>
        </div>
      </div>
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Settings() {
  const [tab, setTab] = useState<Tab>('general')

  return (
    <div className="p-4 md:p-6 max-w-3xl mx-auto space-y-5">
      <div>
        <h1 className="text-xl font-bold text-text-primary">Ajustes</h1>
        <p className="text-sm text-text-muted mt-0.5">Gestiona tu cuenta y espacio de trabajo</p>
      </div>

      <Card padding={false} className="overflow-hidden">
        {/* Tab bar */}
        <div className="flex border-b border-border-subtle overflow-x-auto scrollbar-none">
          {TABS.map(({ id, label, icon: Icon }) => {
            const active = tab === id
            return (
              <button
                key={id}
                onClick={() => setTab(id)}
                className={cn(
                  'relative flex items-center gap-2 px-5 py-3.5 text-sm font-medium whitespace-nowrap transition-colors duration-150',
                  active ? 'text-text-primary' : 'text-text-muted hover:text-text-secondary',
                )}
              >
                <Icon className="w-3.5 h-3.5" />
                {label}
                {active && (
                  <motion.div
                    layoutId="settings-tab-indicator"
                    className="absolute bottom-0 left-0 right-0 h-[2px] bg-accent-blue"
                    transition={{ type: 'spring', stiffness: 420, damping: 36 }}
                  />
                )}
              </button>
            )
          })}
        </div>

        {/* Content */}
        <div className="p-6">
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={tab}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.18, ease: 'easeOut' }}
            >
              {tab === 'general'        && <GeneralTab />}
              {tab === 'notificaciones' && <NotificacionesTab />}
              {tab === 'seguridad'      && <SeguridadTab />}
              {tab === 'equipo'         && <EquipoTab />}
              {tab === 'facturacion'    && <BillingTab />}
            </motion.div>
          </AnimatePresence>
        </div>
      </Card>
    </div>
  )
}
