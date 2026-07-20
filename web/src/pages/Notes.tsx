import { motion, AnimatePresence } from 'framer-motion'
import React, { useState } from 'react'
import {
  Pin, PinOff, Plus, Search, Trash2, X, StickyNote, Pencil, CloudUpload,
} from 'lucide-react'
import Input from '../components/Input'
import Button from '../components/Button'
import Modal from '../components/Modal'
import EmptyState from '../components/EmptyState'
import { CardSkeleton } from '../components/Skeleton'
import { cn } from '../lib/cn'
import { useNotes, useNoteMutations } from '../hooks/useNotes'
import { useToast } from '../components/Toast'
import type { Note } from '../types'

// ── Types ─────────────────────────────────────────────────────────────────────

type NoteColor = Note['color']

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
    label:      'Neutro',
    chip:       'bg-glass-medium border-border-subtle',
  },
  amber: {
    bg:         'bg-amber-500/10',
    border:     'border-amber-500/25',
    titleColor: 'text-amber-600 dark:text-amber-300',
    label:      'Ámbar',
    chip:       'bg-amber-400',
  },
  sky: {
    bg:         'bg-sky-500/10',
    border:     'border-sky-500/25',
    titleColor: 'text-sky-600 dark:text-sky-300',
    label:      'Cielo',
    chip:       'bg-sky-400',
  },
  emerald: {
    bg:         'bg-emerald-500/10',
    border:     'border-emerald-500/25',
    titleColor: 'text-emerald-600 dark:text-emerald-300',
    label:      'Esmeralda',
    chip:       'bg-emerald-400',
  },
  rose: {
    bg:         'bg-rose-500/10',
    border:     'border-rose-500/25',
    titleColor: 'text-rose-600 dark:text-rose-300',
    label:      'Rosa',
    chip:       'bg-rose-400',
  },
}

const NOTE_COLORS: NoteColor[] = ['neutral', 'amber', 'sky', 'emerald', 'rose']

// ── One-shot localStorage migration (carta §6: "migración one-shot de localStorage
// con banner") ──────────────────────────────────────────────────────────────────

const LEGACY_STORAGE_KEY = 'cardeep_notes'

interface LegacyNote { title: string; body: string; color: NoteColor; pinned: boolean }

function readLegacyNotes(): LegacyNote[] {
  try {
    const raw = localStorage.getItem(LEGACY_STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as Partial<LegacyNote>[]
    if (!Array.isArray(parsed)) return []
    return parsed
      .filter(n => n && (n.title || n.body))
      .map(n => ({
        title: n.title ?? '', body: n.body ?? '', color: (n.color as NoteColor) ?? 'neutral', pinned: !!n.pinned,
      }))
  } catch {
    return []
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function timeAgo(iso: string): string {
  const m = Math.floor((Date.now() - new Date(iso).getTime()) / 60000)
  if (m < 1)  return 'Ahora'
  if (m < 60) return `Hace ${m}m`
  const h = Math.floor(m / 60)
  if (h < 24) return `Hace ${h}h`
  return `Hace ${Math.floor(h / 24)}d`
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
      title={isEditing ? 'Editar nota' : 'Nueva nota'}
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
            placeholder="Título de la nota…"
            className={cn(
              'w-full bg-transparent text-base font-bold placeholder:text-text-muted/60 outline-none',
              cfg.titleColor,
            )}
          />
          <textarea
            value={form.body}
            onChange={e => setForm(f => ({ ...f, body: e.target.value }))}
            placeholder="Escribe tu nota…"
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
              Eliminar
            </Button>
          )}
          <Button variant="secondary" size="sm" className="flex-1" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            variant="primary"
            size="sm"
            className="flex-1"
            onClick={handleSave}
            disabled={!form.title.trim() && !form.body.trim()}
          >
            {isEditing ? 'Guardar cambios' : 'Añadir nota'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}

// ── Note card ─────────────────────────────────────────────────────────────────

// forwardRef: AnimatePresence mode="popLayout" attaches a ref to each direct
// child to measure it during exit animations (same fix as Deals' DealRow).
const NoteCard = React.forwardRef<HTMLDivElement, { note: Note; index?: number; onEdit: () => void; onPin: () => void }>(
  function NoteCard({ note, index = 0, onEdit, onPin }, ref) {
  const cfg = COLOR_CONFIG[note.color]
  // Staggered entrance on first mount, capped so a long list doesn't leave the
  // last cards waiting seconds to appear.
  const enterDelay = Math.min(index * 0.04, 0.3)

  return (
    <motion.div
      ref={ref}
      layout
      initial={{ opacity: 0, scale: 0.95, y: 8 }}
      animate={{ opacity: 1, scale: 1,    y: 0 }}
      exit={{ opacity: 0, scale: 0.95, y: 8 }}
      whileHover={{ y: -2 }}
      transition={{
        type: 'spring', stiffness: 380, damping: 26, delay: enterDelay,
        // Layout moves (e.g. reordering into "Fijadas" on toggle) skip the mount
        // delay above — only the initial appear/exit should ever wait.
        layout: { type: 'spring', stiffness: 380, damping: 30 },
      }}
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
          {note.title || <span className="text-text-muted italic font-normal">Sin título</span>}
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
          aria-label={note.pinned ? 'Desfijar nota' : 'Fijar nota'}
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
          <Pencil className="w-2.5 h-2.5" /> Editar
        </span>
      </div>
    </motion.div>
  )
})

// ── Empty editor state ────────────────────────────────────────────────────────

const BLANK_NOTE: EditorState = { title: '', body: '', color: 'neutral' }

// ── Main page ─────────────────────────────────────────────────────────────────

export default function Notes() {
  const { data, error, loading, reload } = useNotes()
  const { createNote, updateNote, deleteNote, loading: mutating } = useNoteMutations()
  const { success, error: toastErr } = useToast()

  // Honest empty array on failure — never a fabricated notebook (carta §4).
  const notes = data?.notes ?? []

  const [search,      setSearch]      = useState('')
  const [editorOpen,  setEditorOpen]  = useState(false)
  const [editorState, setEditorState] = useState<EditorState>(BLANK_NOTE)

  // One-shot localStorage migration banner (carta §6). Only offered once notes have
  // actually loaded AND the server genuinely has none yet — never overwrites real data.
  const [legacyNotes] = useState<LegacyNote[]>(() => readLegacyNotes())
  const [migrating, setMigrating] = useState(false)
  const [migrated, setMigrated] = useState(false)
  const showMigrationBanner = !loading && !error && notes.length === 0 && legacyNotes.length > 0 && !migrated

  async function handleMigrate() {
    setMigrating(true)
    try {
      for (const n of legacyNotes) {
        await createNote({ title: n.title, body: n.body, color: n.color, pinned: n.pinned })
      }
      localStorage.removeItem(LEGACY_STORAGE_KEY)
      setMigrated(true)
      success(`${legacyNotes.length} nota(s) migradas`)
      reload()
    } catch {
      toastErr('No se pudieron migrar todas las notas')
    } finally {
      setMigrating(false)
    }
  }

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

  async function handleSave(data: EditorState) {
    try {
      if (data.id) {
        await updateNote(data.id, { title: data.title, body: data.body, color: data.color })
      } else {
        await createNote({ title: data.title, body: data.body, color: data.color, pinned: false })
      }
      setEditorOpen(false)
      reload()
    } catch {
      toastErr('No se pudo guardar la nota')
    }
  }

  async function handleDelete() {
    if (editorState.id) {
      try {
        await deleteNote(editorState.id)
        reload()
      } catch {
        toastErr('No se pudo eliminar la nota')
      }
    }
    setEditorOpen(false)
  }

  async function handleTogglePin(note: Note) {
    try {
      await updateNote(note.id, { pinned: !note.pinned })
      reload()
    } catch {
      toastErr('No se pudo actualizar la nota')
    }
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
          <h1 className="text-xl font-bold text-text-primary">Notas</h1>
          <p className="text-sm text-text-muted mt-0.5 tabular-nums">
            {notes.length} {notes.length === 1 ? 'nota' : 'notas'} ·&nbsp;
            {notes.filter(n => n.pinned).length} fijada(s)
          </p>
        </div>
        <Button
          size="sm"
          icon={<Plus className="w-4 h-4" />}
          onClick={openNew}
          loading={mutating}
        >
          Nueva nota
        </Button>
      </div>

      {/* One-shot localStorage migration banner (carta §6) */}
      {showMigrationBanner && (
        <motion.div
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative flex items-center gap-3 overflow-hidden rounded-xl glass py-3 pl-4 pr-4"
        >
          <span className="absolute inset-y-0 left-0 w-1 bg-accent-blue" />
          <CloudUpload className="h-4 w-4 shrink-0 text-accent-blue" />
          <p className="flex-1 text-xs text-text-secondary">
            Encontramos <span className="font-semibold text-text-primary tabular-nums">{legacyNotes.length}</span> nota(s) guardadas solo en este dispositivo. Migrarlas para verlas en cualquier equipo.
          </p>
          <Button size="sm" onClick={handleMigrate} loading={migrating}>Migrar ahora</Button>
        </motion.div>
      )}

      {/* Error state — honest failure, never a silently-swapped fallback */}
      {error && (
        <EmptyState
          icon={<StickyNote className="w-6 h-6" />}
          title="No se pudieron cargar las notas"
          message="Hubo un error contactando al servidor."
          action={<Button size="sm" onClick={reload}>Reintentar</Button>}
        />
      )}

      {loading && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {[...Array(8)].map((_, i) => <CardSkeleton key={i} />)}
        </div>
      )}

      {/* Search */}
      {!loading && !error && (
      <Input
        icon={<Search className="w-4 h-4" />}
        placeholder="Buscar notas…"
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
      )}

      {/* Empty state */}
      {!loading && !error && filtered.length === 0 && (
        <EmptyState
          icon={<StickyNote className="w-6 h-6" />}
          title={search ? 'Sin coincidencias' : 'Sin notas todavía'}
          message={
            search
              ? 'Prueba con otro término de búsqueda.'
              : 'Crea tu primera nota para llevar seguimiento de tareas, recordatorios e ideas.'
          }
          action={
            !search ? (
              <Button size="sm" icon={<Plus className="w-4 h-4" />} onClick={openNew}>
                Nueva nota
              </Button>
            ) : undefined
          }
        />
      )}

      {/* Pinned section */}
      <AnimatePresence>
        {!loading && !error && pinned.length > 0 && (
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="flex items-center gap-2 mb-3">
              <Pin className="w-3.5 h-3.5 text-accent-blue" />
              <p className="text-[11px] text-text-muted uppercase tracking-wider font-semibold">
                Fijadas
              </p>
            </div>
            <motion.div
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3"
              layout
            >
              <AnimatePresence mode="popLayout">
                {pinned.map((note, idx) => (
                  <NoteCard
                    key={note.id}
                    note={note}
                    index={idx}
                    onEdit={() => openEdit(note)}
                    onPin={() => handleTogglePin(note)}
                  />
                ))}
              </AnimatePresence>
            </motion.div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* All notes */}
      <AnimatePresence>
        {!loading && !error && unpinned.length > 0 && (
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {pinned.length > 0 && (
              <p className="text-[11px] text-text-muted uppercase tracking-wider font-semibold mb-3">
                Notas
              </p>
            )}
            <motion.div
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3"
              layout
            >
              <AnimatePresence mode="popLayout">
                {unpinned.map((note, idx) => (
                  <NoteCard
                    key={note.id}
                    note={note}
                    index={idx}
                    onEdit={() => openEdit(note)}
                    onPin={() => handleTogglePin(note)}
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
