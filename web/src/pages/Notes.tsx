import { motion, AnimatePresence } from 'framer-motion'
import React, { useState, useCallback } from 'react'
import {
  Pin, PinOff, Plus, Search, Trash2, X, StickyNote, Pencil,
} from 'lucide-react'
import Input from '../components/Input'
import Button from '../components/Button'
import Modal from '../components/Modal'
import EmptyState from '../components/EmptyState'
import { cn } from '../lib/cn'

// ── Types ─────────────────────────────────────────────────────────────────────

type NoteColor = 'neutral' | 'amber' | 'sky' | 'emerald' | 'rose'

interface Note {
  id: string
  title: string
  body: string
  color: NoteColor
  pinned: boolean
  createdAt: string
  updatedAt: string
}

// ── Note color config ─────────────────────────────────────────────────────────

const COLOR_CONFIG: Record<NoteColor, {
  bg: string
  border: string
  titleColor: string
  label: string
  chip: string
}> = {
  neutral: {
    bg:         'bg-glass-subtle',
    border:     'border-border-subtle',
    titleColor: 'text-text-primary',
    label:      'Default',
    chip:       'bg-glass-medium border-border-subtle',
  },
  amber: {
    bg:         'bg-amber-500/10',
    border:     'border-amber-500/25',
    titleColor: 'text-amber-600 dark:text-amber-300',
    label:      'Amber',
    chip:       'bg-amber-400',
  },
  sky: {
    bg:         'bg-sky-500/10',
    border:     'border-sky-500/25',
    titleColor: 'text-sky-600 dark:text-sky-300',
    label:      'Sky',
    chip:       'bg-sky-400',
  },
  emerald: {
    bg:         'bg-emerald-500/10',
    border:     'border-emerald-500/25',
    titleColor: 'text-emerald-600 dark:text-emerald-300',
    label:      'Emerald',
    chip:       'bg-emerald-400',
  },
  rose: {
    bg:         'bg-rose-500/10',
    border:     'border-rose-500/25',
    titleColor: 'text-rose-600 dark:text-rose-300',
    label:      'Rose',
    chip:       'bg-rose-400',
  },
}

const NOTE_COLORS: NoteColor[] = ['neutral', 'amber', 'sky', 'emerald', 'rose']

// ── Sample notes ──────────────────────────────────────────────────────────────

const SAMPLE_NOTES: Note[] = [
  {
    id: 'n1',
    title: 'Call Maria Santos',
    body: 'Discuss BMW 320d pricing — she wants a test drive next Saturday. Check availability and prepare comparison sheet. Preferred: automatic transmission, dark exterior.',
    color: 'sky',
    pinned: true,
    createdAt: '2026-06-28T10:00:00Z',
    updatedAt: '2026-06-28T10:00:00Z',
  },
  {
    id: 'n2',
    title: 'Stock review — end of month',
    body: 'Prepare aging report. 3 vehicles over 60 days need repricing strategy before end of month. BMW 320d (72d), Audi A4 (68d), VW Golf (61d).',
    color: 'rose',
    pinned: true,
    createdAt: '2026-06-27T09:00:00Z',
    updatedAt: '2026-06-27T09:00:00Z',
  },
  {
    id: 'n3',
    title: 'Audi A4 inspection',
    body: 'Book certified mechanic before listing. Target price €31k — cross-check AutoScout24 and mobile.de comps before publishing.',
    color: 'amber',
    pinned: false,
    createdAt: '2026-06-26T14:00:00Z',
    updatedAt: '2026-06-26T14:00:00Z',
  },
  {
    id: 'n4',
    title: 'Follow-up: John Doe',
    body: 'He asked for extended warranty options on the VW Golf. Send comparison sheet by Friday. Budget: up to €28k.',
    color: 'emerald',
    pinned: false,
    createdAt: '2026-06-25T11:00:00Z',
    updatedAt: '2026-06-25T11:00:00Z',
  },
  {
    id: 'n5',
    title: 'Mercedes listing photos',
    body: 'C220 photos scheduled for Tuesday morning. Remind photographer: full interior shots, dashboard, boot space. Uploader after shoot.',
    color: 'neutral',
    pinned: false,
    createdAt: '2026-06-24T16:00:00Z',
    updatedAt: '2026-06-24T16:00:00Z',
  },
  {
    id: 'n6',
    title: 'AutoScout24 ad renewal',
    body: 'Premium listings expire June 30. Renew for BMW X3, Seat Ateca, VW Tiguan. Check ad spend vs conversion for last 30 days before renewing.',
    color: 'neutral',
    pinned: false,
    createdAt: '2026-06-23T08:00:00Z',
    updatedAt: '2026-06-23T08:00:00Z',
  },
]

// ── Local storage hook ────────────────────────────────────────────────────────

function useNotes() {
  const [notes, setNotes] = useState<Note[]>(() => {
    try {
      const raw = localStorage.getItem('cardeep_notes')
      return raw ? (JSON.parse(raw) as Note[]) : SAMPLE_NOTES
    } catch {
      return SAMPLE_NOTES
    }
  })

  const persist = useCallback((next: Note[]) => {
    setNotes(next)
    try { localStorage.setItem('cardeep_notes', JSON.stringify(next)) } catch { /* noop */ }
  }, [])

  function createNote(data: Omit<Note, 'id' | 'createdAt' | 'updatedAt'>): Note {
    const note: Note = {
      ...data,
      id: `n-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    persist([note, ...notes])
    return note
  }

  function updateNote(id: string, patch: Partial<Omit<Note, 'id' | 'createdAt'>>) {
    persist(
      notes.map(n =>
        n.id === id ? { ...n, ...patch, updatedAt: new Date().toISOString() } : n,
      ),
    )
  }

  function deleteNote(id: string) {
    persist(notes.filter(n => n.id !== id))
  }

  function togglePin(id: string) {
    persist(
      notes.map(n =>
        n.id === id ? { ...n, pinned: !n.pinned, updatedAt: new Date().toISOString() } : n,
      ),
    )
  }

  return { notes, createNote, updateNote, deleteNote, togglePin }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function timeAgo(iso: string): string {
  const m = Math.floor((Date.now() - new Date(iso).getTime()) / 60000)
  if (m < 1)  return 'Just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

// ── Color picker ──────────────────────────────────────────────────────────────

function ColorPicker({
  selected,
  onChange,
}: { selected: NoteColor; onChange: (c: NoteColor) => void }) {
  return (
    <div className="flex gap-2 items-center">
      <span className="text-xs text-text-muted">Color</span>
      {NOTE_COLORS.map(c => {
        const cfg = COLOR_CONFIG[c]
        return (
          <button
            key={c}
            type="button"
            title={cfg.label}
            onClick={() => onChange(c)}
            className={cn(
              'w-5 h-5 rounded-full border-2 transition-all',
              cfg.chip,
              selected === c ? 'ring-2 ring-offset-2 ring-accent-blue scale-110' : 'hover:scale-105',
              c === 'neutral' ? 'border-border-default' : 'border-transparent',
            )}
          />
        )
      })}
    </div>
  )
}

// ── Note editor modal ─────────────────────────────────────────────────────────

interface EditorState {
  id?: string
  title: string
  body: string
  color: NoteColor
}

function NoteEditorModal({
  open,
  initial,
  onClose,
  onSave,
  onDelete,
}: {
  open: boolean
  initial: EditorState
  onClose: () => void
  onSave: (data: EditorState) => void
  onDelete?: () => void
}) {
  const [form, setForm] = useState<EditorState>(initial)

  // sync when initial changes (open new vs edit)
  React.useEffect(() => {
    if (open) setForm(initial)
  }, [open, initial])

  function handleSave() {
    if (!form.title.trim() && !form.body.trim()) return
    onSave(form)
  }

  const isEditing = !!initial.id
  const cfg = COLOR_CONFIG[form.color]

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEditing ? 'Edit note' : 'New note'}
      size="sm"
    >
      <div className="space-y-4">
        {/* Color-tinted preview header */}
        <div className={cn('rounded-xl p-4 border', cfg.bg, cfg.border)}>
          <input
            autoFocus
            type="text"
            value={form.title}
            onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
            placeholder="Note title…"
            className={cn(
              'w-full bg-transparent text-base font-bold placeholder:text-text-muted/60 outline-none',
              cfg.titleColor,
            )}
          />
          <textarea
            value={form.body}
            onChange={e => setForm(f => ({ ...f, body: e.target.value }))}
            placeholder="Write your note…"
            rows={5}
            className="w-full mt-2 bg-transparent text-sm text-text-secondary placeholder:text-text-muted/50 outline-none resize-none leading-relaxed"
          />
        </div>

        {/* Color picker */}
        <ColorPicker selected={form.color} onChange={c => setForm(f => ({ ...f, color: c }))} />

        {/* Actions */}
        <div className="flex items-center gap-2 pt-1">
          {onDelete && (
            <Button
              variant="danger"
              size="sm"
              icon={<Trash2 className="w-3.5 h-3.5" />}
              onClick={onDelete}
              className="shrink-0"
            >
              Delete
            </Button>
          )}
          <Button variant="secondary" size="sm" className="flex-1" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            className="flex-1"
            onClick={handleSave}
            disabled={!form.title.trim() && !form.body.trim()}
          >
            {isEditing ? 'Save changes' : 'Add note'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}

// ── Note card ─────────────────────────────────────────────────────────────────

// forwardRef: AnimatePresence mode="popLayout" attaches a ref to each direct
// child to measure it during exit animations (same fix as Deals' DealRow).
const NoteCard = React.forwardRef<HTMLDivElement, { note: Note; onEdit: () => void; onPin: () => void }>(
  function NoteCard({ note, onEdit, onPin }, ref) {
  const cfg = COLOR_CONFIG[note.color]

  return (
    <motion.div
      ref={ref}
      layout
      initial={{ opacity: 0, scale: 0.95, y: 8 }}
      animate={{ opacity: 1, scale: 1,    y: 0 }}
      exit={{ opacity: 0, scale: 0.95, y: 8 }}
      whileHover={{ y: -2 }}
      transition={{ type: 'spring', stiffness: 380, damping: 26 }}
      onClick={onEdit}
      className={cn(
        'rounded-xl border p-4 cursor-pointer group flex flex-col gap-3',
        'transition-shadow hover:shadow-elevation-2',
        cfg.bg, cfg.border,
      )}
    >
      {/* Note header */}
      <div className="flex items-start justify-between gap-2">
        <p className={cn('text-sm font-bold leading-snug flex-1 min-w-0 break-words', cfg.titleColor)}>
          {note.title || <span className="text-text-muted italic font-normal">Untitled</span>}
        </p>
        <button
          type="button"
          onClick={e => { e.stopPropagation(); onPin() }}
          className={cn(
            'p-1 rounded-md transition-all shrink-0',
            note.pinned
              ? 'text-accent-blue opacity-100'
              : 'text-text-muted opacity-0 group-hover:opacity-100 hover:text-text-primary',
          )}
          aria-label={note.pinned ? 'Unpin note' : 'Pin note'}
        >
          {note.pinned ? (
            <Pin className="w-3.5 h-3.5" />
          ) : (
            <PinOff className="w-3.5 h-3.5" />
          )}
        </button>
      </div>

      {/* Note body */}
      {note.body && (
        <p className="text-xs text-text-secondary leading-relaxed line-clamp-4 flex-1">
          {note.body}
        </p>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between mt-auto pt-1">
        <span className="text-[10px] text-text-muted tabular-nums">
          {timeAgo(note.updatedAt)}
        </span>
        <span className="flex items-center gap-1 text-[10px] text-text-muted opacity-0 group-hover:opacity-100 transition-opacity">
          <Pencil className="w-2.5 h-2.5" /> Edit
        </span>
      </div>
    </motion.div>
  )
})

// ── Empty editor state ────────────────────────────────────────────────────────

const BLANK_NOTE: EditorState = { title: '', body: '', color: 'neutral' }

// ── Main page ─────────────────────────────────────────────────────────────────

export default function Notes() {
  const { notes, createNote, updateNote, deleteNote, togglePin } = useNotes()
  const [search,      setSearch]      = useState('')
  const [editorOpen,  setEditorOpen]  = useState(false)
  const [editorState, setEditorState] = useState<EditorState>(BLANK_NOTE)

  // Filter
  const filtered = search.trim()
    ? notes.filter(n =>
        `${n.title} ${n.body}`.toLowerCase().includes(search.toLowerCase()),
      )
    : notes

  const pinned   = filtered.filter(n => n.pinned)
  const unpinned = filtered.filter(n => !n.pinned)

  function openNew() {
    setEditorState(BLANK_NOTE)
    setEditorOpen(true)
  }

  function openEdit(note: Note) {
    setEditorState({ id: note.id, title: note.title, body: note.body, color: note.color })
    setEditorOpen(true)
  }

  function handleSave(data: EditorState) {
    if (data.id) {
      updateNote(data.id, { title: data.title, body: data.body, color: data.color })
    } else {
      createNote({ title: data.title, body: data.body, color: data.color, pinned: false })
    }
    setEditorOpen(false)
  }

  function handleDelete() {
    if (editorState.id) {
      deleteNote(editorState.id)
    }
    setEditorOpen(false)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="p-4 md:p-6 max-w-7xl mx-auto space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-text-primary">Notes</h1>
          <p className="text-sm text-text-muted mt-0.5">
            {notes.length} {notes.length === 1 ? 'note' : 'notes'} ·&nbsp;
            {notes.filter(n => n.pinned).length} pinned
          </p>
        </div>
        <Button
          size="sm"
          icon={<Plus className="w-4 h-4" />}
          onClick={openNew}
        >
          New note
        </Button>
      </div>

      {/* Search */}
      <Input
        icon={<Search className="w-4 h-4" />}
        placeholder="Search notes…"
        value={search}
        onChange={e => setSearch(e.target.value)}
        iconRight={
          search ? (
            <button
              type="button"
              onClick={() => setSearch('')}
              className="text-text-muted hover:text-text-primary transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          ) : undefined
        }
      />

      {/* Empty state */}
      {filtered.length === 0 && (
        <EmptyState
          icon={<StickyNote className="w-6 h-6" />}
          title={search ? 'No notes match' : 'No notes yet'}
          message={
            search
              ? 'Try a different search term.'
              : 'Create your first note to keep track of follow-ups, reminders and ideas.'
          }
          action={
            !search ? (
              <Button size="sm" icon={<Plus className="w-4 h-4" />} onClick={openNew}>
                New note
              </Button>
            ) : undefined
          }
        />
      )}

      {/* Pinned section */}
      <AnimatePresence>
        {pinned.length > 0 && (
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="flex items-center gap-2 mb-3">
              <Pin className="w-3.5 h-3.5 text-accent-blue" />
              <p className="text-[11px] text-text-muted uppercase tracking-wider font-semibold">
                Pinned
              </p>
            </div>
            <motion.div
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3"
              layout
            >
              <AnimatePresence mode="popLayout">
                {pinned.map(note => (
                  <NoteCard
                    key={note.id}
                    note={note}
                    onEdit={() => openEdit(note)}
                    onPin={() => togglePin(note.id)}
                  />
                ))}
              </AnimatePresence>
            </motion.div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* All notes */}
      <AnimatePresence>
        {unpinned.length > 0 && (
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {pinned.length > 0 && (
              <p className="text-[11px] text-text-muted uppercase tracking-wider font-semibold mb-3">
                Notes
              </p>
            )}
            <motion.div
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3"
              layout
            >
              <AnimatePresence mode="popLayout">
                {unpinned.map(note => (
                  <NoteCard
                    key={note.id}
                    note={note}
                    onEdit={() => openEdit(note)}
                    onPin={() => togglePin(note.id)}
                  />
                ))}
              </AnimatePresence>
            </motion.div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* Create / Edit modal */}
      <NoteEditorModal
        open={editorOpen}
        initial={editorState}
        onClose={() => setEditorOpen(false)}
        onSave={handleSave}
        onDelete={editorState.id ? handleDelete : undefined}
      />
    </motion.div>
  )
}
