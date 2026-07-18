import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronLeft, ChevronRight, Plus, Clock, User2, Download, Trash2 } from 'lucide-react'
import Card from '../components/Card'
import { Badge } from '../components/Badge'
import Button from '../components/Button'
import Input from '../components/Input'
import Select from '../components/Select'
import Modal from '../components/Modal'
import EmptyState from '../components/EmptyState'
import LoadingSpinner from '../components/LoadingSpinner'
import { cn } from '../lib/cn'
import { useCalendarEvents, useCalendarEventMutations, icsDownloadUrl } from '../hooks/useCalendarEvents'
import { useApi } from '../hooks/useApi'
import { useToast } from '../components/Toast'
import { getStoredToken } from '../api/client'
import type { CalEvent, Contact } from '../types'

// 06-unified-crm-chat F6: real per-tenant persistence (crm_event) — replaces the
// previous hardcoded event list + dead "New event" button.

const TYPE_COLOR: Record<CalEvent['type'], NonNullable<Parameters<typeof Badge>[0]['color']>> = {
  visit: 'blue',
  call: 'green',
  reminder: 'yellow',
  delivery: 'purple',
}

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

function isoDate(d: Date) {
  return d.toISOString().split('T')[0]
}

function weekdayOf(d: Date) {
  return (d.getDay() + 6) % 7
}

function daysInMonth(year: number, month: number) {
  return new Date(year, month + 1, 0).getDate()
}

// Export requires a Bearer token; a plain <a href> can't set headers, so fetch the
// .ics with auth and trigger the download from the resulting blob.
async function downloadIcs(eventId: string, title: string) {
  const token = getStoredToken()
  const res = await fetch(icsDownloadUrl(eventId), {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (!res.ok) return
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${title.replace(/[^a-z0-9]+/gi, '_') || 'event'}.ics`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

interface ContactListResponse { contacts: Contact[]; total: number }

// ── New event modal ───────────────────────────────────────────────────────────

function NewEventModal({
  open, onClose, onCreated, defaultDate,
}: { open: boolean; onClose: () => void; onCreated: () => void; defaultDate: string }) {
  const { data: contactData } = useApi<ContactListResponse>(open ? '/contacts' : '')
  const { createEvent, loading } = useCalendarEventMutations()
  const { success, error: toastErr } = useToast()
  const contacts = contactData?.contacts ?? []

  const [title, setTitle] = useState('')
  const [date, setDate] = useState(defaultDate)
  const [time, setTime] = useState('10:00')
  const [type, setType] = useState<CalEvent['type']>('visit')
  const [location, setLocation] = useState('')
  const [contactId, setContactId] = useState('')
  const [formError, setFormError] = useState<string | null>(null)

  React.useEffect(() => { if (open) setDate(defaultDate) }, [open, defaultDate])

  function reset() {
    setTitle(''); setTime('10:00'); setType('visit'); setLocation(''); setContactId(''); setFormError(null)
  }

  function handleClose() { reset(); onClose() }

  async function handleSave() {
    if (!title.trim() || !date) return
    setFormError(null)
    try {
      const startsAt = new Date(`${date}T${time}:00`).toISOString()
      await createEvent({
        title: title.trim(), startsAt, type, location: location.trim() || undefined,
        contactId: contactId || undefined,
      })
      success('Event created')
      onCreated()
      reset()
      onClose()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create event'
      setFormError(message)
      toastErr(message)
    }
  }

  return (
    <Modal open={open} onClose={handleClose} title="New Event" size="sm">
      <div className="space-y-4">
        <Input label="Title" placeholder="Visita de Juan · BMW 320d" value={title} onChange={e => setTitle(e.target.value)} autoFocus />
        <div className="grid grid-cols-2 gap-3">
          <Input label="Date" type="date" value={date} onChange={e => setDate(e.target.value)} />
          <Input label="Time" type="time" value={time} onChange={e => setTime(e.target.value)} />
        </div>
        <Select
          label="Type"
          value={type}
          onChange={e => setType(e.target.value as CalEvent['type'])}
          options={[
            { value: 'visit', label: 'Visit' },
            { value: 'call', label: 'Call' },
            { value: 'reminder', label: 'Reminder' },
            { value: 'delivery', label: 'Delivery' },
          ]}
        />
        <Input label="Location (optional)" value={location} onChange={e => setLocation(e.target.value)} />
        {contacts.length > 0 && (
          <Select
            label="Contact (optional)"
            placeholder="—"
            value={contactId}
            onChange={e => setContactId(e.target.value)}
            options={contacts.map(c => ({ value: c.id, label: c.name }))}
          />
        )}
        {formError && <p className="text-xs text-accent-rose">{formError}</p>}
        <div className="flex gap-2 pt-1">
          <Button variant="secondary" size="sm" className="flex-1" onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="primary" size="sm" className="flex-1"
            onClick={handleSave} disabled={!title.trim()} loading={loading}
          >
            Create
          </Button>
        </div>
      </div>
    </Modal>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function Calendar() {
  const now = new Date()
  const [year, setYear]             = useState(now.getFullYear())
  const [month, setMonth]           = useState(now.getMonth())
  const [selectedDate, setSelected] = useState(isoDate(now))
  const [newEventOpen, setNewEventOpen] = useState(false)
  const { deleteEvent } = useCalendarEventMutations()
  const { success, error: toastErr } = useToast()

  function prev() {
    if (month === 0) { setYear((y) => y - 1); setMonth(11) }
    else setMonth((m) => m - 1)
  }
  function next() {
    if (month === 11) { setYear((y) => y + 1); setMonth(0) }
    else setMonth((m) => m + 1)
  }

  const firstDay  = new Date(year, month, 1)
  const totalDays = daysInMonth(year, month)
  const startPad  = weekdayOf(firstDay)

  const cells: (number | null)[] = [
    ...Array<null>(startPad).fill(null),
    ...Array.from({ length: totalDays }, (_, i) => i + 1),
  ]

  const monthStartIso = new Date(year, month, 1).toISOString()
  const monthEndIso   = new Date(year, month + 1, 0, 23, 59, 59).toISOString()
  const { data, loading, error, reload } = useCalendarEvents(monthStartIso, monthEndIso)
  // Honest empty array on failure — never a fabricated agenda (carta §4).
  const events = data?.events ?? []

  const eventsByDate: Record<string, CalEvent[]> = {}
  for (const e of events) {
    const dateKey = e.startsAt.split('T')[0]
    if (!eventsByDate[dateKey]) eventsByDate[dateKey] = []
    eventsByDate[dateKey].push(e)
  }

  const selectedEvents = eventsByDate[selectedDate] ?? []
  const monthLabel     = new Date(year, month).toLocaleDateString('en-GB', {
    month: 'long', year: 'numeric',
  })

  async function handleDeleteEvent(id: string) {
    try {
      await deleteEvent(id)
      success('Event deleted')
      reload()
    } catch {
      toastErr('Failed to delete event')
    }
  }

  return (
    <div className="p-4 md:p-6 max-w-4xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-text-primary">Calendar</h1>
          <p className="text-sm text-text-muted mt-0.5">{monthLabel}</p>
        </div>
        <button
          onClick={() => setNewEventOpen(true)}
          className={cn(
            'flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium',
            'bg-accent-blue text-white shadow-glow-blue hover:brightness-110',
            'transition-[filter] duration-150 min-h-[36px]',
          )}
        >
          <Plus className="w-3.5 h-3.5" /> New event
        </button>
      </div>

      {error && (
        <EmptyState
          icon={<Clock className="w-6 h-6" />}
          title="No se pudo cargar el calendario"
          message="Hubo un error contactando al servidor."
          action={<Button size="sm" onClick={reload}>Reintentar</Button>}
        />
      )}

      {!error && (
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Month grid */}
          <Card className="flex-1">
            {/* Month navigation */}
            <div className="flex items-center justify-between mb-5">
              <button
                onClick={prev}
                className="w-8 h-8 flex items-center justify-center rounded-lg text-text-muted hover:text-text-primary hover:bg-glass-medium transition-colors duration-150"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <h2 className="text-sm font-semibold text-text-primary flex items-center gap-2">
                {monthLabel}
                {loading && <LoadingSpinner size="sm" />}
              </h2>
              <button
                onClick={next}
                className="w-8 h-8 flex items-center justify-center rounded-lg text-text-muted hover:text-text-primary hover:bg-glass-medium transition-colors duration-150"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            {/* Day-of-week headers */}
            <div className="grid grid-cols-7 mb-2">
              {DAYS.map((d) => (
                <div key={d} className="text-center text-[10px] font-semibold text-text-muted uppercase py-1 tracking-wider">
                  {d}
                </div>
              ))}
            </div>

            {/* Calendar cells */}
            <div className="grid grid-cols-7 gap-1">
              {cells.map((day, idx) => {
                if (!day) return <div key={`pad-${idx}`} />

                const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
                const dayEvents = eventsByDate[dateStr] ?? []
                const isToday = dateStr === isoDate(now)
                const isSel   = dateStr === selectedDate

                return (
                  <button
                    key={dateStr}
                    onClick={() => setSelected(dateStr)}
                    className={cn(
                      'relative aspect-square flex flex-col items-center justify-center rounded-xl text-xs',
                      'transition-all duration-150 cursor-pointer',
                      isSel
                        ? 'bg-accent-blue text-white shadow-glow-blue'
                        : isToday
                        ? 'ring-1 ring-accent-blue/50 text-accent-blue font-semibold bg-accent-blue/10'
                        : 'text-text-secondary hover:bg-glass-medium hover:text-text-primary',
                    )}
                  >
                    <span className="font-medium">{day}</span>
                    {dayEvents.length > 0 && (
                      <span
                        className={cn(
                          'w-1 h-1 rounded-full mt-0.5',
                          isSel ? 'bg-white/70' : 'bg-accent-blue',
                        )}
                      />
                    )}
                  </button>
                )
              })}
            </div>
          </Card>

          {/* Day panel */}
          <Card className="lg:w-64 shrink-0">
            <h3 className="text-sm font-semibold text-text-primary mb-4">
              {new Date(selectedDate + 'T12:00:00').toLocaleDateString('en-GB', {
                weekday: 'long', day: 'numeric', month: 'short',
              })}
            </h3>

            <AnimatePresence mode="wait" initial={false}>
              <motion.div
                key={selectedDate}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.18, ease: 'easeOut' }}
              >
                {selectedEvents.length === 0 ? (
                  <p className="text-xs text-text-muted py-6 text-center">No events scheduled</p>
                ) : (
                  <div className="space-y-3">
                    {selectedEvents.map((e) => (
                      <div
                        key={e.id}
                        className="p-3 rounded-xl border border-border-subtle bg-glass-subtle space-y-2"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-xs font-medium text-text-primary leading-snug">{e.title}</p>
                          <Badge color={TYPE_COLOR[e.type]} className="shrink-0 !text-[10px]">
                            {e.type}
                          </Badge>
                        </div>
                        <div className="flex flex-col gap-1">
                          <span className="flex items-center gap-1 text-[10px] text-text-muted">
                            <Clock className="w-3 h-3" />
                            {new Date(e.startsAt).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}
                          </span>
                          {e.contactName && (
                            <span className="flex items-center gap-1 text-[10px] text-text-muted">
                              <User2 className="w-3 h-3" /> {e.contactName}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-3 pt-1">
                          <button
                            onClick={() => downloadIcs(e.id, e.title)}
                            className="flex items-center gap-1 text-[10px] text-accent-blue hover:underline"
                          >
                            <Download className="w-3 h-3" /> .ics
                          </button>
                          <button
                            onClick={() => handleDeleteEvent(e.id)}
                            className="flex items-center gap-1 text-[10px] text-text-muted hover:text-rose-400 transition-colors"
                          >
                            <Trash2 className="w-3 h-3" /> Delete
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </Card>
        </div>
      )}

      <NewEventModal
        open={newEventOpen}
        onClose={() => setNewEventOpen(false)}
        onCreated={reload}
        defaultDate={selectedDate}
      />
    </div>
  )
}
