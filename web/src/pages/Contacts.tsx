import { motion, AnimatePresence } from 'framer-motion'
import React, { useState } from 'react'
import {
  Search, Phone, Mail, Users, LayoutGrid, List,
  ChevronRight, X, UserPlus, Briefcase, Calendar,
} from 'lucide-react'
import Input from '../components/Input'
import Avatar from '../components/Avatar'
import { Badge } from '../components/Badge'
import EmptyState from '../components/EmptyState'
import Timeline from '../components/Timeline'
import Modal from '../components/Modal'
import Button from '../components/Button'
import { cn } from '../lib/cn'
import { useApi } from '../hooks/useApi'
import type { Contact, Activity } from '../types'
import type { TimelineItem } from '../components/Timeline'

interface ContactList   { contacts: Contact[]; total: number }
interface ContactDetail { contact: Contact; activities: Activity[] }

// ── Mock data ─────────────────────────────────────────────────────────────────

const MOCK_CONTACTS: Contact[] = Array.from({ length: 12 }, (_, i) => ({
  id: `c${i}`,
  tenantId: 't1',
  name: [
    'Maria Santos', 'John Doe', 'Anna Weber', 'Peter Klein', 'Sophie Leblanc',
    'Hans Müller', 'Clara Rossi', 'Tom Brown', 'Lisa Chen', 'David Novak',
    'Eva Fischer', 'Carlos Mora',
  ][i],
  email: [
    'maria.santos@example.com', 'john.doe@example.com', 'anna.weber@example.com',
    'p.klein@example.com', 'sophie.l@example.com', 'hans.m@example.com',
    'c.rossi@example.com', 'tom.b@example.com', 'lisa.chen@example.com',
    'd.novak@example.com', 'eva.fischer@example.com', 'c.mora@example.com',
  ][i],
  phone: [
    '+49 170 481 2001', '+44 7700 900 123', '+49 151 234 5678',
    '+49 163 987 6543', '+33 6 12 34 56 78', '+49 176 555 1234',
    '+39 347 123 4567', '+44 7911 123 456', '+49 170 876 5432',
    '+420 601 234 567', '+49 163 456 7890', '+34 612 345 678',
  ][i],
  createdAt: new Date(Date.now() - i * 86400000 * 14).toISOString(),
  updatedAt: new Date(Date.now() - i * 86400000 * (i % 3 + 1)).toISOString(),
  dealCount: [3, 0, 2, 1, 0, 4, 0, 1, 2, 0, 1, 3][i],
}))

const MOCK_ACTIVITIES: Activity[] = [
  {
    id: 'a1', tenantId: 't', dealId: 'd1', type: 'call',
    body: 'Discussed BMW 320d pricing — interested at €26k. Wants Saturday test drive.',
    createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
  },
  {
    id: 'a2', tenantId: 't', dealId: 'd1', type: 'inquiry',
    body: 'Requested full service history report and CARFAX check.',
    createdAt: new Date(Date.now() - 86400000 * 5).toISOString(),
  },
  {
    id: 'a3', tenantId: 't', dealId: 'd1', type: 'note',
    body: 'Prefers automatic transmission, dark exterior. Budget flexible up to €30k.',
    createdAt: new Date(Date.now() - 86400000 * 9).toISOString(),
  },
]

// ── Helpers ───────────────────────────────────────────────────────────────────

function contactTag(c: Contact): 'client' | 'lead' {
  return (c.dealCount ?? 0) > 0 ? 'client' : 'lead'
}

function timeAgo(iso: string): string {
  const m = Math.floor((Date.now() - new Date(iso).getTime()) / 60000)
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

const activityAccent: Record<Activity['type'], TimelineItem['accent']> = {
  inquiry: 'blue', reply: 'blue', call: 'green',
  visit: 'green', note: 'yellow', reminder: 'yellow',
}
const activityBadgeColor: Record<Activity['type'], 'blue' | 'green' | 'yellow' | 'orange'> = {
  inquiry: 'blue', reply: 'blue', call: 'green',
  visit: 'green', note: 'yellow', reminder: 'orange',
}

// ── Stats bar ─────────────────────────────────────────────────────────────────

function StatsBar({ contacts }: { contacts: Contact[] }) {
  const clients    = contacts.filter(c => contactTag(c) === 'client').length
  const leads      = contacts.length - clients
  const totalDeals = contacts.reduce((s, c) => s + (c.dealCount ?? 0), 0)

  const stats = [
    { label: 'Total',   value: contacts.length, accent: 'text-text-primary'   },
    { label: 'Clients', value: clients,          accent: 'text-accent-blue'    },
    { label: 'Leads',   value: leads,            accent: 'text-text-secondary' },
    { label: 'Deals',   value: totalDeals,       accent: 'text-accent-emerald' },
  ]

  return (
    <div className="grid grid-cols-4 rounded-xl overflow-hidden border border-border-subtle divide-x divide-border-subtle">
      {stats.map(s => (
        <div key={s.label} className="flex flex-col items-center py-3.5 px-2 bg-glass-subtle">
          <span className={cn('text-2xl font-bold tabular-nums leading-none mb-1', s.accent)}>
            {s.value}
          </span>
          <span className="text-[10px] text-text-muted uppercase tracking-wider">{s.label}</span>
        </div>
      ))}
    </div>
  )
}

// ── Contact list row ──────────────────────────────────────────────────────────

function ContactRow({
  contact, selected, onClick,
}: { contact: Contact; selected: boolean; onClick: () => void }) {
  const tag = contactTag(contact)
  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full flex items-center gap-3 px-4 py-3 text-left transition-all duration-150',
        'border-l-2 hover:bg-glass-medium',
        selected ? 'bg-accent-blue/5 border-accent-blue' : 'border-transparent',
      )}
    >
      <Avatar name={contact.name} size="sm" />

      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-text-primary truncate">{contact.name}</p>
        <p className="text-xs text-text-muted truncate mt-0.5">{contact.email}</p>
      </div>

      <div className="hidden md:flex flex-col items-end gap-0.5 shrink-0">
        <p className="text-xs text-text-secondary font-mono">{contact.phone}</p>
        <p className="text-[10px] text-text-muted">{timeAgo(contact.updatedAt)}</p>
      </div>

      <Badge color={tag === 'client' ? 'blue' : 'gray'} dot>
        {tag === 'client' ? 'Client' : 'Lead'}
      </Badge>

      <ChevronRight className="w-4 h-4 text-text-muted shrink-0" />
    </button>
  )
}

// ── Contact grid card ─────────────────────────────────────────────────────────

function ContactCard({
  contact, onClick,
}: { contact: Contact; onClick: () => void }) {
  const tag = contactTag(contact)
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ y: -2 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      onClick={onClick}
      className="glass rounded-xl p-4 cursor-pointer flex flex-col gap-3 group"
    >
      <div className="flex items-start justify-between gap-2">
        <Avatar name={contact.name} size="md" />
        <Badge color={tag === 'client' ? 'blue' : 'gray'} dot>
          {tag === 'client' ? 'Client' : 'Lead'}
        </Badge>
      </div>

      <div className="min-w-0">
        <p className="text-sm font-semibold text-text-primary truncate group-hover:text-accent-blue transition-colors">
          {contact.name}
        </p>
        <p className="text-xs text-text-muted truncate mt-0.5">{contact.email}</p>
        <p className="text-xs text-text-muted/70 truncate mt-0.5 font-mono">{contact.phone}</p>
      </div>

      <div className="flex items-center justify-between pt-2.5 border-t border-border-subtle">
        {(contact.dealCount ?? 0) > 0 ? (
          <span className="text-xs font-semibold text-accent-blue">
            {contact.dealCount} {contact.dealCount === 1 ? 'deal' : 'deals'}
          </span>
        ) : (
          <span className="text-xs text-text-muted">No deals</span>
        )}
        <span className="text-[10px] text-text-muted">{timeAgo(contact.updatedAt)}</span>
      </div>
    </motion.div>
  )
}

// ── Contact detail drawer ─────────────────────────────────────────────────────

function ContactDrawer({
  contact, activities, onClose,
}: { contact: Contact | null; activities: Activity[]; onClose: () => void }) {
  const tag = contact ? contactTag(contact) : 'lead'

  const timelineItems: TimelineItem[] = activities.map(a => ({
    id:     a.id,
    date:   formatDate(a.createdAt),
    title:  a.body,
    accent: activityAccent[a.type] ?? 'gray',
    badge:  <Badge color={activityBadgeColor[a.type] ?? 'gray'}>{a.type}</Badge>,
  }))

  return (
    <AnimatePresence>
      {contact && (
        <>
          <motion.div
            key="cd-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="fixed inset-0 bg-black/30 backdrop-blur-[2px] z-[180]"
            onClick={onClose}
          />

          <motion.aside
            key="cd-panel"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 340, damping: 34 }}
            className="fixed right-0 inset-y-0 w-full max-w-[360px] z-[181] flex flex-col overflow-hidden"
            style={{
              background: 'var(--bg-surface)',
              borderLeft: '1px solid var(--border-subtle)',
              boxShadow: '-4px 0 32px rgba(0,0,0,0.18)',
            }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-border-subtle shrink-0">
              <h2 className="text-sm font-semibold text-text-primary truncate">{contact.name}</h2>
              <motion.button
                whileTap={{ scale: 0.9 }}
                onClick={onClose}
                className="p-1.5 rounded-md hover:bg-glass-medium text-text-muted hover:text-text-primary transition-colors shrink-0 ml-2"
              >
                <X className="w-4 h-4" />
              </motion.button>
            </div>

            {/* Body */}
            <div className="flex-1 overflow-y-auto p-5 space-y-6">
              {/* Profile hero */}
              <div className="flex flex-col items-center text-center gap-3 py-2">
                <Avatar name={contact.name} size="lg" />
                <div>
                  <p className="text-base font-bold text-text-primary">{contact.name}</p>
                  <div className="mt-2 flex justify-center">
                    <Badge color={tag === 'client' ? 'blue' : 'gray'} dot>
                      {tag === 'client' ? 'Client' : 'Lead'}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Contact info */}
              <div className="space-y-2">
                <p className="text-[10px] text-text-muted uppercase tracking-wider font-semibold px-1">
                  Contact info
                </p>
                <a
                  href={`mailto:${contact.email}`}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-lg glass text-sm text-text-secondary hover:text-accent-blue transition-colors group"
                >
                  <Mail className="w-3.5 h-3.5 shrink-0 text-text-muted group-hover:text-accent-blue transition-colors" />
                  <span className="truncate">{contact.email}</span>
                </a>
                <a
                  href={`tel:${contact.phone}`}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-lg glass text-sm text-text-secondary hover:text-accent-blue transition-colors group font-mono"
                >
                  <Phone className="w-3.5 h-3.5 shrink-0 text-text-muted group-hover:text-accent-blue transition-colors font-sans" />
                  <span>{contact.phone}</span>
                </a>
              </div>

              {/* Stats grid */}
              <div className="grid grid-cols-2 gap-2">
                {[
                  {
                    icon: <Briefcase className="w-3.5 h-3.5 text-text-muted" />,
                    label: 'Deals',
                    value: String(contact.dealCount ?? 0),
                  },
                  {
                    icon: <Calendar className="w-3.5 h-3.5 text-text-muted" />,
                    label: 'Last contact',
                    value: timeAgo(contact.updatedAt),
                  },
                  {
                    icon: <Calendar className="w-3.5 h-3.5 text-text-muted" />,
                    label: 'Customer since',
                    value: formatDate(contact.createdAt),
                  },
                  {
                    icon: <Users className="w-3.5 h-3.5 text-text-muted" />,
                    label: 'Status',
                    value: tag === 'client' ? 'Client' : 'Lead',
                  },
                ].map(item => (
                  <div key={item.label} className="glass rounded-lg p-3">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      {item.icon}
                      <p className="text-[10px] text-text-muted uppercase tracking-wider">{item.label}</p>
                    </div>
                    <p className="text-sm font-semibold text-text-primary">{item.value}</p>
                  </div>
                ))}
              </div>

              {/* Timeline */}
              <div>
                <p className="text-[10px] text-text-muted uppercase tracking-wider font-semibold px-1 mb-3">
                  Activity
                </p>
                {timelineItems.length > 0 ? (
                  <Timeline items={timelineItems} />
                ) : (
                  <p className="text-sm text-text-muted italic px-1">No activities yet.</p>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="px-4 py-3 border-t border-border-subtle shrink-0 flex gap-2">
              <Button
                variant="primary"
                size="sm"
                className="flex-1"
                icon={<Phone className="w-3.5 h-3.5" />}
              >
                Call
              </Button>
              <Button
                variant="secondary"
                size="sm"
                className="flex-1"
                icon={<Mail className="w-3.5 h-3.5" />}
              >
                Email
              </Button>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}

// ── New contact modal ─────────────────────────────────────────────────────────

function NewContactModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [name,  setName]  = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')

  function handleClose() {
    setName(''); setEmail(''); setPhone('')
    onClose()
  }

  return (
    <Modal open={open} onClose={handleClose} title="New Contact" size="sm">
      <div className="space-y-4">
        <Input
          label="Full name"
          placeholder="Maria Santos"
          value={name}
          onChange={e => setName(e.target.value)}
          autoFocus
        />
        <Input
          label="Email"
          type="email"
          placeholder="maria@example.com"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        <Input
          label="Phone"
          type="tel"
          placeholder="+49 170 000 0000"
          value={phone}
          onChange={e => setPhone(e.target.value)}
        />
        <div className="flex gap-2 pt-1">
          <Button variant="secondary" size="sm" className="flex-1" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            className="flex-1"
            onClick={handleClose}
            disabled={!name.trim()}
          >
            Save contact
          </Button>
        </div>
      </div>
    </Modal>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function Contacts() {
  const [search,     setSearch]     = useState('')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [viewMode,   setViewMode]   = useState<'list' | 'grid'>('list')
  const [newOpen,    setNewOpen]    = useState(false)

  const { data }        = useApi<ContactList>('/contacts')
  const contacts        = data?.contacts ?? MOCK_CONTACTS

  const { data: detail } = useApi<ContactDetail>(
    selectedId ? `/contacts/${selectedId}` : '',
    [selectedId],
  )

  const filtered = search.trim()
    ? contacts.filter(c =>
        `${c.name} ${c.email} ${c.phone}`.toLowerCase().includes(search.toLowerCase()),
      )
    : contacts

  const selected = contacts.find(c => c.id === selectedId) ?? null

  function handleRowClick(id: string) {
    setSelectedId(prev => (prev === id ? null : id))
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-4 md:p-6 max-w-7xl mx-auto space-y-5"
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-text-primary">Contacts</h1>
          <p className="text-sm text-text-muted mt-0.5">
            {contacts.length} contacts in CRM
          </p>
        </div>
        <Button
          size="sm"
          icon={<UserPlus className="w-4 h-4" />}
          onClick={() => setNewOpen(true)}
        >
          New contact
        </Button>
      </div>

      {/* Stats */}
      <StatsBar contacts={contacts} />

      {/* Search + view toggle */}
      <div className="flex gap-3 items-center">
        <Input
          icon={<Search className="w-4 h-4" />}
          placeholder="Search by name, email or phone…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="flex-1"
        />
        <div className="flex gap-0.5 glass rounded-lg p-1 shrink-0">
          <button
            onClick={() => setViewMode('list')}
            className={cn(
              'p-1.5 rounded-md transition-colors',
              viewMode === 'list'
                ? 'bg-glass-strong text-text-primary'
                : 'text-text-muted hover:text-text-secondary',
            )}
            aria-label="List view"
          >
            <List className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode('grid')}
            className={cn(
              'p-1.5 rounded-md transition-colors',
              viewMode === 'grid'
                ? 'bg-glass-strong text-text-primary'
                : 'text-text-muted hover:text-text-secondary',
            )}
            aria-label="Grid view"
          >
            <LayoutGrid className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {filtered.length === 0 ? (
          <EmptyState
            key="empty"
            icon={<Users className="w-6 h-6" />}
            title="No contacts found"
            message="Try adjusting your search or add a new contact."
            action={
              <Button size="sm" icon={<UserPlus className="w-4 h-4" />} onClick={() => setNewOpen(true)}>
                Add contact
              </Button>
            }
          />
        ) : viewMode === 'grid' ? (
          <motion.div
            key="grid"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3"
          >
            {filtered.map((c, i) => (
              <motion.div
                key={c.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
              >
                <ContactCard contact={c} onClick={() => handleRowClick(c.id)} />
              </motion.div>
            ))}
          </motion.div>
        ) : (
          <motion.div
            key="list"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="glass rounded-xl overflow-hidden"
          >
            {/* Table header */}
            <div className="hidden md:grid grid-cols-[auto_1fr_auto_auto_auto] gap-3 items-center px-4 py-2.5 border-b border-border-subtle">
              <div className="w-8" />
              <p className="text-[10px] text-text-muted uppercase tracking-wider font-semibold">Name</p>
              <p className="text-[10px] text-text-muted uppercase tracking-wider font-semibold">Phone</p>
              <p className="text-[10px] text-text-muted uppercase tracking-wider font-semibold">Status</p>
              <div className="w-4" />
            </div>
            <div className="divide-y divide-border-subtle">
              {filtered.map((c, idx) => (
                <motion.div
                  key={c.id}
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.025 }}
                >
                  <ContactRow
                    contact={c}
                    selected={selectedId === c.id}
                    onClick={() => handleRowClick(c.id)}
                  />
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Detail drawer */}
      <ContactDrawer
        contact={selected}
        activities={detail?.activities ?? MOCK_ACTIVITIES}
        onClose={() => setSelectedId(null)}
      />

      {/* New contact modal */}
      <NewContactModal open={newOpen} onClose={() => setNewOpen(false)} />
    </motion.div>
  )
}
