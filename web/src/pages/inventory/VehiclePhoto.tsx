import { useState } from 'react'
import { Car } from 'lucide-react'

// Deterministic dark gradient per make — used as a fallback placeholder when
// photo_url is null or the hotlinked image 404s. Intentionally dark in BOTH
// themes (same precedent as the old thumbnail treatment: a photo placeholder
// should never look like a blank light rectangle).
export const MAKE_GRAD: Record<string, [string, string]> = {
  Ford: ['#111a2e', '#0a1020'],
  FORD: ['#111a2e', '#0a1020'],
  SEAT: ['#1a1408', '#0e0a02'],
  BMW: ['#0a1020', '#050a16'],
  Fiat: ['#1a0a0a', '#100404'],
  Citroen: ['#0a1a14', '#04120a'],
  Peugeot: ['#12101a', '#0a0812'],
  'DS Automobiles': ['#160a1a', '#0c0512'],
}
export const DEFAULT_GRAD: [string, string] = ['#12121e', '#0a0a14']

interface VehiclePhotoProps {
  photoUrl: string | null
  make: string | null
  className?: string
  style?: React.CSSProperties
}

export default function VehiclePhoto({ photoUrl, make, className, style }: VehiclePhotoProps) {
  const [failed, setFailed] = useState(false)
  const showPlaceholder = !photoUrl || failed
  const [g1, g2] = (make && MAKE_GRAD[make]) ?? DEFAULT_GRAD

  if (showPlaceholder) {
    return (
      <div
        className={className}
        style={{
          width: '100%', height: '100%', position: 'relative', overflow: 'hidden',
          background: `linear-gradient(135deg, ${g1} 0%, ${g2} 100%)`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          ...style,
        }}
      >
        <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 30% 45%, rgba(255,255,255,0.05) 0%, transparent 60%)' }} />
        <Car style={{ width: '28%', height: '28%', opacity: 0.14, color: '#fff' }} strokeWidth={1.1} />
        {make && (
          <span style={{ position: 'absolute', bottom: 8, left: 10, fontSize: 10, fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.14)' }}>
            {make}
          </span>
        )}
      </div>
    )
  }

  return (
    <img
      src={photoUrl}
      alt=""
      loading="lazy"
      decoding="async"
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
      className={className}
      style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block', ...style }}
    />
  )
}
