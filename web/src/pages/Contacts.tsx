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
import { Skeleton, CardSkeleton, TableSkeleton } from '../components/Skeleton'
import { cn } from '../lib/cn'
import { useApi } from '../hooks/useApi'
import { useContactMutations } from '../hooks/useContacts'
import { useToast } from '../components/Toast'
import { ApiError } from '../api/client'
import type { Contact, Activity } from '../types'
import type { TimelineItem } from '../components/Timeline'

interface ContactList   { contacts: Contact[]; total: number }
interface ContactDetail { contact: Contact; activities: Activity[] }

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
      {stats.map((s, i) => (
        <motion.div
          key={s.label}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05, duration: 0.25 }}
          className="flex flex-col items-center py-3.5 px-2 bg-glass-subtle"
        >
          <span className={cn('text-2xl font-bold tabular-nums leading-none mb-1', s.accent)}>
            {s.value}
          </span>
          <span className="text-[10px] text-text-muted uppercase tracking-wider">{s.label}</span>
        </motion.div>
      ))}
    </div>
  )
}

function StatsBarSkeleton() {
  return (
    <div className="grid grid-cols-4 rounded-xl overflow-hidden border border-border-subtle divide-x divide-border-subtle">
      {[0, 1, 2, 3].map(i => (
        <div key={i} className="flex flex-col items-center gap-2 py-4 px-2 bg-glass-subtle">
          <Skeleton className="h-6 w-9" />
          <Skeleton className="h-2 w-12" />
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
        <p className="text-xs text-text-secondary font-mono tabular-nums">{contact.phone}</p>
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
      role="button"
      tabIndex={0}
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      onClick={onClick}
      onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick() } }}
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
        <p className="text-xs text-text-muted/70 truncate mt-0.5 font-mono tabular-nums">{contact.phone}</p>
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
                  className="flex items-center gap-3 px-3 py-2.5 rounded-lg glass text-sm text-text-secondary hover:text-accent-blue transition-colors group font-mono tabular-nums"
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
                ].map((item, i) => (
                  <motion.div
                    key={item.label}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.04, duration: 0.22 }}
                    className="glass rounded-lg p-3"
                  >
                    <div className="flex items-center gap-1.5 mb-1.5">
                      {item.icon}
                      <p className="text-[10px] text-text-muted uppercase tracking-wider">{item.label}</p>
                    </div>
                    <p className="text-sm font-semibold text-text-primary tabular-nums">{item.value}</p>
                  </motion.div>
                ))}
              </div>

              {/* Timeline */}
              <div>
                <p className="text-[10px] text-text-muted uppercase tracking-wider font-semibold px-1 mb-3">
                  Activity
                </p>
                <Timeline items={timelineItems} emptyMessage="No activities yet." />
              </div>
            </div>

            {/* Footer — anti-decorative-button (carta §1): real tel:/mailto: navigation,
                the minimum functional floor until F4's in-app channel exists. */}
            <div className="px-4 py-3 border-t border-border-subtle shrink-0 flex gap-2">
              <Button
                variant="primary"
                size="sm"
                className="flex-1"
                icon={<Phone className="w-3.5 h-3.5" />}
                disabled={!contact.phone}
                onClick={() => { if (contact.phone) window.location.href = `tel:${contact.phone}` }}
              >
                Call
              </Button>
              <Button
                variant="secondary"
                size="sm"
                className="flex-1"
                icon={<Mail className="w-3.5 h-3.5" />}
                disabled={!contact.email}
                onClick={() => { if (contact.email) window.location.href = `mailto:${contact.email}` }}
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

function NewContactModal({
  open, onClose, onCreated,
}: { open: boolean; onClose: () => void; onCreated: () => void }) {
  const [name,  setName]  = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const { createContact, loading } = useContactMutations()
  const { success, error: toastErr } = useToast()

  function reset() {
    setName(''); setEmail(''); setPhone(''); setFormError(null)
  }

  function handleClose() {
    reset()
    onClose()
  }

  // Anti-decorative-button (carta §1, "Save contact" POST real; modal NO cierra hasta
  // 201; error -> mensaje visible): the modal only closes on a confirmed 201 from the
  // server — never on a blind click.
  async function handleSave() {
    if (!name.trim()) return
    setFormError(null)
    try {
      await createContact({
        name: name.trim(),
        email: email.trim() || undefined,
        phone: phone.trim() || undefined,
      })
      success('Contact saved')
      onCreated()
      reset()
      onClose()
    } catch (err) {
      const message = err instanceof ApiError
        ? (err.status === 409 ? 'A contact with this phone or email already exists' : err.message)
        : 'Failed to save contact'
      setFormError(message)
      toastErr(message)
    }
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
          placeholder="612 345 678"
          value={phone}
          onChange={e => setPhone(e.target.value)}
        />
        {formError && (
          <p className="text-xs text-accent-rose">{formError}</p>
        )}
        <div className="flex gap-2 pt-1">
          <Button variant="secondary" size="sm" className="flex-1" onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            className="flex-1"
            onClick={handleSave}
            disabled={!name.trim()}
            loading={loading}
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

  const { data, error, loading, reload } = useApi<ContactList>('/contacts')
  // Honest empty array on failure — never a fabricated roster (carta §4 "Regla
  // transversal de honestidad de producto": ningun fallback simulado en ninguna pagina CRM).
  const contacts        = data?.contacts ?? []
  // Distinguishes "still waiting on the first response" from "server answered
  // with zero rows" — without this, the empty state would flash on every cold
  // load before real data (or a real empty roster) arrives.
  const initialLoading  = loading && !data

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
          {initialLoading ? (
            <Skeleton className="h-4 w-32 mt-1.5" />
          ) : (
            <p className="text-sm text-text-muted mt-0.5">
              {contacts.length} contacts in CRM
            </p>
          )}
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
      {initialLoading ? <StatsBarSkeleton /> : <StatsBar contacts={contacts} />}

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
          <motion.button
            whileHover={{ scale: 1.06 }}
            whileTap={{ scale: 0.92 }}
            transition={{ type: 'spring', stiffness: 400, damping: 20 }}
            onClick={() => setViewMode('list')}
            className={cn(
              'p-1.5 rounded-md transition-colors',
              viewMode === 'list'
                ? 'bg-glass-strong text-text-primary'
                : 'text-text-muted hover:text-text-secondary',
            )}
            aria-label="List view"
            aria-pressed={viewMode === 'list'}
          >
            <List className="w-4 h-4" />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.06 }}
            whileTap={{ scale: 0.92 }}
            transition={{ type: 'spring', stiffness: 400, damping: 20 }}
            onClick={() => setViewMode('grid')}
            className={cn(
              'p-1.5 rounded-md transition-colors',
              viewMode === 'grid'
                ? 'bg-glass-strong text-text-primary'
                : 'text-text-muted hover:text-text-secondary',
            )}
            aria-label="Grid view"
            aria-pressed={viewMode === 'grid'}
          >
            <LayoutGrid className="w-4 h-4" />
          </motion.button>
        </div>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {initialLoading ? (
          viewMode === 'grid' ? (
            <motion.div
              key="loading-grid"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3"
            >
              {[...Array(8)].map((_, i) => <CardSkeleton key={i} />)}
            </motion.div>
          ) : (
            <motion.div
              key="loading-list"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="glass rounded-xl p-4"
            >
              <TableSkeleton rows={6} />
            </motion.div>
          )
        ) : filtered.length === 0 ? (
          <EmptyState
            key="empty"
            icon={<Users className="w-6 h-6" />}
            title={error ? 'No se pudo cargar los contactos' : 'No contacts found'}
            message={
              error
                ? 'Hubo un error contactando al servidor. Reintenta.'
                : 'Try adjusting your search or add a new contact.'
            }
            action={
              error ? (
                <Button size="sm" onClick={reload}>Reintentar</Button>
              ) : (
                <Button size="sm" icon={<UserPlus className="w-4 h-4" />} onClick={() => setNewOpen(true)}>
                  Add contact
                </Button>
              )
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
        activities={detail?.activities ?? []}
        onClose={() => setSelectedId(null)}
      />

      {/* New contact modal */}
      <NewContactModal open={newOpen} onClose={() => setNewOpen(false)} onCreated={reload} />
    </motion.div>
  )
}
