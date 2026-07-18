// K15 — every target-price change is captured WITH a categorized reason (closes
// the Tekion "override gap" cited in carta §2.1). This form is the ONLY path to
// POST /dealer/vehicles/{ulid}/price-override — reason_category is required by
// both this UI and the backend's pydantic model, never optional.
import { useState } from 'react'
import { X } from 'lucide-react'
import type { VehicleListItem } from '../../api/cardeep'
import Modal from '../../components/Modal'
import Input from '../../components/Input'
import Button from '../../components/Button'
import { useToast } from '../../components/Toast'
import { formatPrice } from './derive'

const REASON_OPTIONS = [
  { value: 'reposicionamiento_mercado', label: 'Reposicionamiento vs mercado' },
  { value: 'urgencia_liquidez', label: 'Necesidad de liquidez' },
  { value: 'defecto_detectado', label: 'Defecto/incidencia detectada' },
  { value: 'estrategia_temporada', label: 'Estrategia de temporada' },
  { value: 'otro', label: 'Otro' },
] as const

interface PriceOverrideFormProps {
  vehicle: VehicleListItem
  onClose: () => void
  onSubmit: (targetPrice: number, reasonCategory: string) => Promise<void>
}

export default function PriceOverrideForm({ vehicle, onClose, onSubmit }: PriceOverrideFormProps) {
  const [targetPrice, setTargetPrice] = useState(vehicle.price ? String(vehicle.price) : '')
  const [reason, setReason] = useState<string>('')
  const [submitting, setSubmitting] = useState(false)
  const { error: toastError, success } = useToast()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    const parsed = Number(targetPrice)
    if (!Number.isFinite(parsed) || parsed < 0) { toastError('Precio objetivo inválido'); return }
    if (!reason) { toastError('Selecciona una razón — obligatoria (K15)'); return }
    setSubmitting(true)
    try {
      await onSubmit(parsed, reason)
      success('Precio objetivo actualizado')
    } catch {
      toastError('No se pudo guardar el precio objetivo')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal open onClose={onClose} size="sm" title="Fijar precio objetivo">
      <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <p style={{ fontSize: 12.5, color: 'var(--t3)' }}>
          {vehicle.title ?? `${vehicle.make} ${vehicle.model}`} · anunciado a {formatPrice(vehicle.price, vehicle.currency)}
        </p>
        <Input
          label="Precio objetivo (€)"
          type="number"
          min={0}
          value={targetPrice}
          onChange={e => setTargetPrice(e.target.value)}
          required
        />
        <div>
          <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--t3)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.02em' }}>
            Razón del cambio (obligatoria)
          </label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {REASON_OPTIONS.map(opt => (
              <label key={opt.value} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12.5, color: 'var(--t2)', cursor: 'pointer' }}>
                <input type="radio" name="reason" value={opt.value} checked={reason === opt.value} onChange={() => setReason(opt.value)} />
                {opt.label}
              </label>
            ))}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          <Button type="button" variant="ghost" onClick={onClose} icon={<X style={{ width: 13, height: 13 }} />}>Cancelar</Button>
          <Button type="submit" loading={submitting}>Guardar</Button>
        </div>
      </form>
    </Modal>
  )
}
