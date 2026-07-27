import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, X, ChevronDown, Mail, Phone, MessageCircle } from 'lucide-react'
import Card from '../components/Card'
import Button from '../components/Button'
import Input from '../components/Input'
import Select from '../components/Select'
import Modal from '../components/Modal'
import { Badge } from '../components/Badge'
import { useToast } from '../components/Toast'
import { cn } from '../lib/cn'

// ── Types & mock data ─────────────────────────────────────────────────────────

interface Ticket {
  id: string
  number: string
  subject: string
  status: 'open' | 'pending' | 'resolved'
  priority: 'high' | 'medium' | 'low'
  createdAt: string
  updatedAt: string
}

interface FaqItem {
  id: string
  question: string
  answer: string
}

const TICKETS: Ticket[] = [
  { id: 't1', number: '#2041', subject: 'Error al sincronizar stock con AutoScout24',   status: 'open',     priority: 'high',   createdAt: '28 Jun 2026', updatedAt: 'Hace 2h'  },
  { id: 't2', number: '#2038', subject: 'Los PDFs de oferta no se generan correctamente', status: 'pending',  priority: 'medium', createdAt: '25 Jun 2026', updatedAt: 'Hace 1d'  },
  { id: 't3', number: '#2031', subject: 'Duda sobre la configuración de notificaciones',  status: 'pending',  priority: 'low',    createdAt: '20 Jun 2026', updatedAt: 'Hace 3d'  },
  { id: 't4', number: '#2018', subject: 'Exportación de inventario a Excel',              status: 'resolved', priority: 'low',    createdAt: '10 Jun 2026', updatedAt: 'Hace 12d' },
]

const FAQ_ITEMS: FaqItem[] = [
  {
    id: 'f1',
    question: '¿Cómo añado un nuevo vehículo al stock?',
    answer: 'Ve a la sección Vehículos y haz clic en "Añadir vehículo". Puedes introducir el VIN para autocompletar los datos técnicos, el precio y la fuente de adquisición.',
  },
  {
    id: 'f2',
    question: '¿Puedo conectar más de una plataforma de anuncios?',
    answer: 'Sí. En Ajustes → General → Integraciones puedes conectar mobile.de, AutoScout24, leboncoin, La Centrale y otras plataformas compatibles según tu plan contratado.',
  },
  {
    id: 'f3',
    question: '¿Cómo funcionan las alertas de stock parado?',
    answer: 'CARDEEP detecta automáticamente los vehículos con más de 60 días sin movimiento y te notifica por email o in-app según tus preferencias. Puedes ajustar el umbral en Ajustes → Notificaciones.',
  },
  {
    id: 'f4',
    question: '¿Cómo exporto los datos para mi contabilidad?',
    answer: 'En la sección Finanzas puedes exportar el P&L y las transacciones en CSV o XLSX. Los PDFs de cada operación se generan desde la ficha del trato correspondiente.',
  },
  {
    id: 'f5',
    question: '¿Qué ocurre si supero el límite de vehículos de mi plan?',
    answer: 'Recibirás una alerta cuando alcances el 80% del límite. Al superarlo no podrás añadir nuevos vehículos hasta que actualices tu plan o liberes espacios archivando stock.',
  },
]

const TICKET_STATUS: Record<Ticket['status'], { color: 'blue' | 'yellow' | 'green'; label: string }> = {
  open:     { color: 'blue',   label: 'Abierto'   },
  pending:  { color: 'yellow', label: 'Pendiente' },
  resolved: { color: 'green',  label: 'Resuelto'  },
}

const TICKET_PRIORITY: Record<Ticket['priority'], { color: 'red' | 'yellow' | 'gray'; label: string }> = {
  high:   { color: 'red',    label: 'Alta'  },
  medium: { color: 'yellow', label: 'Media' },
  low:    { color: 'gray',   label: 'Baja'  },
}

// ── Ticket row ────────────────────────────────────────────────────────────────
// A real <button> with a real onOpen handler — the old markup had cursor-pointer
// + hover feedback wired to nothing, a fake affordance. Clicking now opens the
// detail modal below, using only fields already present on the ticket.

function TicketRow({ ticket, border, onOpen, delay }: { ticket: Ticket; border: boolean; onOpen: () => void; delay: number }) {
  const status   = TICKET_STATUS[ticket.status]
  const priority = TICKET_PRIORITY[ticket.priority]

  return (
    <motion.button
      type="button"
      onClick={onOpen}
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.25, ease: 'easeOut' }}
      className={cn(
        'w-full flex items-center gap-4 px-5 py-4 text-left',
        'hover:bg-glass-subtle focus-visible:bg-glass-subtle transition-colors duration-150',
        border && 'border-b border-border-subtle',
      )}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-text-muted shrink-0">{ticket.number}</span>
          <p className="text-sm font-medium text-text-primary truncate">{ticket.subject}</p>
        </div>
        <p className="text-xs text-text-muted mt-0.5">
          Creado: {ticket.createdAt} · Actualizado: {ticket.updatedAt}
        </p>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <Badge color={priority.color}>{priority.label}</Badge>
        <Badge color={status.color} dot>{status.label}</Badge>
      </div>
    </motion.button>
  )
}

// ── Ticket detail modal ───────────────────────────────────────────────────────

function TicketDetailModal({ ticket, onClose }: { ticket: Ticket | null; onClose: () => void }) {
  const status   = ticket ? TICKET_STATUS[ticket.status]   : null
  const priority = ticket ? TICKET_PRIORITY[ticket.priority] : null

  return (
    <Modal open={!!ticket} onClose={onClose} title={ticket ? `Ticket ${ticket.number}` : undefined} size="sm">
      {ticket && status && priority && (
        <div className="space-y-4">
          <p className="text-sm font-medium text-text-primary leading-relaxed">{ticket.subject}</p>
          <div className="flex items-center gap-2">
            <Badge color={priority.color}>{priority.label}</Badge>
            <Badge color={status.color} dot>{status.label}</Badge>
          </div>
          <p className="text-xs text-text-muted">
            Creado: {ticket.createdAt} · Actualizado: {ticket.updatedAt}
          </p>
          <Button variant="ghost" size="sm" onClick={onClose}>Cerrar</Button>
        </div>
      )}
    </Modal>
  )
}

// ── FAQ accordion item ────────────────────────────────────────────────────────

function FaqAccordionItem({ item }: { item: FaqItem }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="border-b border-border-subtle last:border-0">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between py-4 text-left gap-4"
      >
        <span className="text-sm font-medium text-text-primary">{item.question}</span>
        <ChevronDown
          className={cn(
            'w-4 h-4 text-text-muted shrink-0 transition-transform duration-200',
            open && 'rotate-180',
          )}
        />
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.22, ease: [0.32, 0.72, 0, 1] }}
            className="overflow-hidden"
          >
            <p className="pb-4 text-sm text-text-secondary leading-relaxed">{item.answer}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ── New ticket form ───────────────────────────────────────────────────────────

function NewTicketForm({ onClose }: { onClose: () => void }) {
  const { success } = useToast()
  const [subject,  setSubject]  = useState('')
  const [priority, setPriority] = useState('medium')
  const [body,     setBody]     = useState('')

  function submit() {
    success('Ticket creado. Recibirás respuesta en menos de 24h.')
    setSubject('')
    setPriority('medium')
    setBody('')
    onClose()
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.22, ease: 'easeOut' }}
    >
      <Card>
        <h3 className="text-sm font-semibold text-text-primary mb-5">Nuevo ticket de soporte</h3>
        <div className="space-y-4 max-w-lg">
          <Input
            label="Asunto"
            placeholder="Describe brevemente el problema"
            value={subject}
            onChange={e => setSubject(e.target.value)}
          />
          <Select
            label="Prioridad"
            value={priority}
            onChange={e => setPriority(e.target.value)}
            options={[
              { value: 'high',   label: 'Alta — Bloquea mi trabajo'        },
              { value: 'medium', label: 'Media — Funcionalidad limitada'   },
              { value: 'low',    label: 'Baja — Consulta o sugerencia'     },
            ]}
          />
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1.5 uppercase tracking-wide">
              Descripción
            </label>
            <textarea
              value={body}
              onChange={e => setBody(e.target.value)}
              placeholder="Describe el problema con detalle: pasos para reproducirlo, mensajes de error, capturas de pantalla…"
              rows={4}
              className={cn(
                'w-full px-3.5 py-2.5 rounded-md text-sm text-text-primary placeholder:text-text-muted',
                'bg-glass-subtle border border-border-subtle resize-none',
                'focus:outline-none focus:ring-2 focus:ring-accent-blue/30 focus:border-border-active',
                'transition-all duration-200',
              )}
            />
          </div>
          <div className="flex gap-3">
            <Button onClick={submit} disabled={!subject.trim() || !body.trim()}>
              Enviar ticket
            </Button>
            <Button variant="ghost" onClick={onClose}>
              Cancelar
            </Button>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}

// ── Contact cards ─────────────────────────────────────────────────────────────

interface ContactItem {
  icon: React.ElementType
  label: string
  value: string
  note: string
  /** mailto:/tel: — a real action for channels that support one; omitted for
   * Chat, which has no live channel wired up (no fake click affordance). */
  href?: string
  live?: boolean
}

const CONTACT_ITEMS: ContactItem[] = [
  { icon: Mail,          label: 'Email',        value: 'soporte@cardeep.ai', note: 'Respuesta en menos de 24h',        href: 'mailto:soporte@cardeep.ai' },
  { icon: Phone,         label: 'Teléfono',     value: '+34 900 123 456',    note: 'Lun–Vie · 9:00–18:00 (CET)',       href: 'tel:+34900123456' },
  { icon: MessageCircle, label: 'Chat en vivo', value: 'Disponible ahora',   note: 'Tiempo medio de respuesta: 5 min', live: true },
]

// ── Page ──────────────────────────────────────────────────────────────────────

export default function Support() {
  const [showNew, setShowNew] = useState(false)
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null)

  const openCount = TICKETS.filter(t => t.status !== 'resolved').length

  return (
    <div className="p-4 md:p-6 max-w-3xl mx-auto space-y-5">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
        className="flex items-start justify-between gap-4"
      >
        <div>
          <h1 className="text-xl font-bold text-text-primary">Soporte</h1>
          <p className="text-sm text-text-muted mt-0.5">Consulta tus tickets o abre uno nuevo</p>
        </div>
        <Button
          variant={showNew ? 'secondary' : 'primary'}
          icon={showNew ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
          onClick={() => setShowNew(v => !v)}
        >
          {showNew ? 'Cerrar formulario' : 'Nuevo ticket'}
        </Button>
      </motion.div>

      {/* New ticket form */}
      <AnimatePresence>
        {showNew && <NewTicketForm onClose={() => setShowNew(false)} />}
      </AnimatePresence>

      {/* Ticket list */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.06, duration: 0.35, ease: 'easeOut' }}
      >
        <Card padding={false} className="overflow-hidden">
          <div className="flex items-center justify-between px-5 py-4 border-b border-border-subtle">
            <h2 className="text-sm font-semibold text-text-primary">Mis tickets</h2>
            {openCount > 0 && (
              <Badge color="blue" dot pulse>{openCount} abierto{openCount > 1 ? 's' : ''}</Badge>
            )}
          </div>
          <div>
            {TICKETS.map((t, i) => (
              <TicketRow
                key={t.id}
                ticket={t}
                border={i < TICKETS.length - 1}
                delay={i * 0.05}
                onOpen={() => setSelectedTicket(t)}
              />
            ))}
          </div>
        </Card>
      </motion.div>

      {/* FAQ */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.12, duration: 0.35, ease: 'easeOut' }}
      >
        <Card>
          <h2 className="text-sm font-semibold text-text-primary">Preguntas frecuentes</h2>
          <p className="text-xs text-text-muted mt-0.5 mb-5">Respuestas a las dudas más comunes</p>
          <div>
            {FAQ_ITEMS.map(item => (
              <FaqAccordionItem key={item.id} item={item} />
            ))}
          </div>
        </Card>
      </motion.div>

      {/* Contact cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {CONTACT_ITEMS.map(({ icon: Icon, label, value, note, href, live }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.18 + i * 0.06, duration: 0.3, ease: 'easeOut' }}
          >
            <Card
              hover={!!href}
              onClick={href ? () => { window.location.href = href } : undefined}
              className="flex flex-col gap-3"
            >
              <div className="w-8 h-8 rounded-lg bg-accent-blue/10 flex items-center justify-center shrink-0">
                <Icon className="w-4 h-4 text-accent-blue" />
              </div>
              <div>
                <p className="text-2xs font-semibold text-text-muted uppercase tracking-wider">{label}</p>
                {live ? (
                  <Badge color="green" dot pulse className="mt-1">{value}</Badge>
                ) : (
                  <p className="text-sm font-semibold text-text-primary mt-0.5">{value}</p>
                )}
                <p className="text-xs text-text-muted mt-0.5">{note}</p>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      <TicketDetailModal ticket={selectedTicket} onClose={() => setSelectedTicket(null)} />
    </div>
  )
}
