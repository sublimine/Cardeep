// 03-garage-fleet F1 — shown instead of "Mi flota" when the logged-in account has
// no dealer tenant yet (role != 'dealer', or role='dealer' but dealer_membership is
// empty). Wires the REAL primitive AUTH-0 built: POST /auth/claim-dealer requires a
// tax ID that (a) passes its own BOE checksum and (b) matches the census's
// entity.cif for the given cdp_code — this is the actual "usuario logueado -> su
// propio cdp_code" mechanism, not a placeholder screen.
import { useState } from 'react'
import { ShieldCheck, Building2 } from 'lucide-react'
import Input from '../../components/Input'
import Button from '../../components/Button'
import { api, ApiError } from '../../api/client'
import { useAuthContext } from '../../auth/AuthContext'

export default function ClaimDealerPrompt() {
  const { refreshUser } = useAuthContext()
  const [cdpCode, setCdpCode] = useState('')
  const [taxId, setTaxId] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await api.post('/auth/claim-dealer', { cdp_code: cdpCode.trim(), tax_id: taxId.trim() })
      await refreshUser()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo verificar el concesionario')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ maxWidth: 460, margin: '64px auto', padding: '0 20px' }}>
      <div className="glass-md glass-edge" style={{ borderRadius: 18, padding: '28px 26px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: 'var(--glass-xs)', border: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Building2 style={{ width: 17, height: 17, color: 'var(--t2)' }} />
          </div>
          <h1 style={{ fontSize: 18, fontWeight: 800, color: 'var(--t1)' }}>Reclama tu concesionario</h1>
        </div>
        <p style={{ fontSize: 13, color: 'var(--t3)', marginBottom: 20, lineHeight: 1.5 }}>
          Introduce el código CDP de tu entidad (censado por CARDEEP) y tu CIF/NIF registrado.
          Verificamos que coincide con el registro censal antes de darte acceso a tu flota real.
        </p>
        <form onSubmit={onSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Input
            label="Código CDP"
            placeholder="CDP-ES-28-XXXXXXXX"
            value={cdpCode}
            onChange={e => setCdpCode(e.target.value)}
            required
          />
          <Input
            label="CIF / NIF"
            placeholder="B12345674"
            value={taxId}
            onChange={e => setTaxId(e.target.value)}
            required
          />
          {error && <p style={{ fontSize: 12.5, color: 'var(--c-rose)' }}>{error}</p>}
          <Button type="submit" loading={submitting} icon={<ShieldCheck style={{ width: 14, height: 14 }} />}>
            Verificar y acceder
          </Button>
        </form>
      </div>
    </div>
  )
}
