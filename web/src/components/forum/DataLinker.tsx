// 08-forum-community F5: DataLinker — "vincular dato" search against the real inventory
// (carta §6.3: "no pega URLs: selecciona la entidad"). Shared by the composer
// (CommunityThread.tsx) and the new-thread modal (Community.tsx, for price_check's
// obligatory anchor).
import { useCallback, useState } from 'react'
import { Link2 } from 'lucide-react'
import { forumApi, type AnchorCandidate, type AnchorInput } from '../../api/forum'

export function DataLinker({ onSelect, label = 'Vincular dato' }: { onSelect: (a: AnchorInput) => void; label?: string }) {
  const [open, setOpen] = useState(false)
  const [q, setQ] = useState('')
  const [results, setResults] = useState<AnchorCandidate[]>([])
  const [searching, setSearching] = useState(false)

  const search = useCallback(async (query: string) => {
    if (query.trim().length < 2) { setResults([]); return }
    setSearching(true)
    try {
      const { data } = await forumApi.anchorSearch(query.trim(), 'vehicle')
      setResults(data)
    } finally {
      setSearching(false)
    }
  }, [])

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-[11.5px] font-medium"
        style={{ border: '1px solid var(--border-subtle)', color: 'var(--text-primary)' }}
      >
        <Link2 className="h-3.5 w-3.5" /> {label}
      </button>
      {open && (
        <div className="absolute z-20 mt-1 w-80 rounded-lg p-3" style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)', boxShadow: '0 8px 24px rgba(0,0,0,0.16)' }}>
          <input
            autoFocus
            className="w-full rounded-md px-2.5 py-1.5 text-sm"
            style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', color: 'var(--text-primary)' }}
            placeholder="Busca un vehículo real (marca, modelo)…"
            value={q}
            onChange={(e) => { setQ(e.target.value); void search(e.target.value) }}
          />
          <div className="mt-2 max-h-56 space-y-1 overflow-y-auto">
            {searching && <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>Buscando…</div>}
            {!searching && results.length === 0 && q.trim().length >= 2 && (
              <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>Sin resultados en el censo.</div>
            )}
            {results.map((r) => (
              <button
                key={r.anchor_ref}
                onClick={() => { onSelect({ anchor_type: r.anchor_type, anchor_ref: r.anchor_ref }); setOpen(false); setQ(''); setResults([]) }}
                className="block w-full rounded-md px-2 py-1.5 text-left text-[12px] hover:bg-[var(--bg-surface)]"
                style={{ color: 'var(--text-primary)' }}
              >
                {r.label}{r.price != null ? ` · ${r.price.toLocaleString('es-ES')} €` : ''}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
