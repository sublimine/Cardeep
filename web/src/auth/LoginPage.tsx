import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useAuthContext } from './AuthContext'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { Mail, Lock, Eye, EyeOff } from 'lucide-react'
import { cn } from '../lib/cn'
import Input from '../components/Input'
import Button from '../components/Button'

// ─── Theme hook ───────────────────────────────────────────────────────────────

function useIsDark(): boolean {
  const [dark, setDark] = useState(
    () => !document.documentElement.classList.contains('light'),
  )
  useEffect(() => {
    const obs = new MutationObserver(
      () => setDark(!document.documentElement.classList.contains('light')),
    )
    obs.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    })
    return () => obs.disconnect()
  }, [])
  return dark
}

// ─── Shared: form card surface ───────────────────────────────────────────────

export function FormCard({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="rounded-2xl border border-border-subtle p-8"
      style={{
        background: 'var(--bg-elevated)',
        boxShadow: 'var(--glass-shadow)',
      }}
    >
      {children}
    </div>
  )
}

// ─── Shared: password input with show/hide toggle ────────────────────────────

export function PasswordInput({
  label,
  value,
  onChange,
  placeholder = '••••••••',
  autoComplete = 'current-password',
  error,
}: {
  label: string
  value: string
  onChange: (v: string) => void
  placeholder?: string
  autoComplete?: string
  error?: string
}) {
  const [show, setShow] = useState(false)
  const fieldId = label.toLowerCase().replace(/\s+/g, '-')

  return (
    <div className="w-full">
      <label
        htmlFor={fieldId}
        className="block text-xs font-medium text-text-secondary mb-1.5 uppercase tracking-wide"
      >
        {label}
      </label>
      <motion.div
        animate={error ? { x: [0, -4, 4, -3, 3, 0] } : { x: 0 }}
        transition={{ duration: 0.35, ease: 'easeInOut' }}
        className="relative"
      >
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none">
          <Lock className="w-4 h-4" />
        </span>
        <input
          id={fieldId}
          type={show ? 'text' : 'password'}
          autoComplete={autoComplete}
          required
          value={value}
          onChange={e => onChange(e.target.value)}
          placeholder={placeholder}
          className={cn(
            'w-full pl-9 pr-10 py-2.5 rounded-md text-sm text-text-primary placeholder:text-text-muted',
            'bg-glass-subtle border transition-all duration-200',
            'focus:outline-none focus:ring-2 focus:ring-offset-0',
            error
              ? 'border-accent-rose focus:ring-accent-rose/30 focus:border-accent-rose'
              : 'border-border-subtle focus:ring-accent-blue/30 focus:border-border-active',
          )}
        />
        <button
          type="button"
          onClick={() => setShow(s => !s)}
          tabIndex={-1}
          aria-label={show ? 'Ocultar contraseña' : 'Mostrar contraseña'}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary transition-colors"
        >
          {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
        </button>
      </motion.div>
      {error && (
        <motion.p
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-1.5 text-xs text-accent-rose"
        >
          {error}
        </motion.p>
      )}
    </div>
  )
}

// ─── Shared: two-column auth layout ──────────────────────────────────────────

export function AuthSplitLayout({ children }: { children: React.ReactNode }) {
  const dark = useIsDark()

  const leftBg = dark
    ? 'linear-gradient(145deg, #0b0b1e 0%, #0e0e24 50%, #12122c 100%)'
    : 'linear-gradient(145deg, #EEF0F3 0%, #E8EDF3 50%, #E0E6EE 100%)'

  return (
    <div
      className="min-h-screen flex font-sans"
      style={{ background: 'var(--bg-primary)', transition: 'background 0.3s' }}
    >
      {/* ── Left panel — brand / claim ─────────────────────────────── */}
      <div
        className="hidden lg:flex flex-col justify-between relative overflow-hidden"
        style={{ flex: '0 0 52%', background: leftBg, padding: '44px 52px' }}
      >
        {/* Blue orb — top-right */}
        <div
          className="pointer-events-none absolute"
          style={{
            top: -100,
            right: -100,
            width: 500,
            height: 500,
            borderRadius: '50%',
            background: `radial-gradient(circle, rgba(59,130,246,${dark ? '0.20' : '0.11'}) 0%, transparent 70%)`,
          }}
        />
        {/* Teal orb — bottom-left */}
        <div
          className="pointer-events-none absolute"
          style={{
            bottom: -80,
            left: -80,
            width: 360,
            height: 360,
            borderRadius: '50%',
            background: `radial-gradient(circle, rgba(8,145,178,${dark ? '0.14' : '0.07'}) 0%, transparent 70%)`,
          }}
        />
        {/* Dot grid texture */}
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            backgroundImage: 'radial-gradient(circle, currentColor 1px, transparent 1px)',
            backgroundSize: '28px 28px',
            color: dark ? 'rgba(255,255,255,0.055)' : 'rgba(20,28,40,0.055)',
          }}
        />

        {/* Logo — top */}
        <div className="relative z-10 flex items-center gap-2.5">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
            <path
              d="M5 17H3a2 2 0 01-2-2V5a2 2 0 012-2h11a2 2 0 012 2v3"
              stroke="#3B82F6"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <rect
              x="9"
              y="11"
              width="14"
              height="10"
              rx="2"
              stroke="#3B82F6"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span
            className="text-xl font-bold"
            style={{ color: 'var(--t1)', letterSpacing: '-0.035em' }}
          >
            cardeep
          </span>
        </div>

        {/* Claim — center */}
        <div className="relative z-10 flex-1 flex flex-col justify-center py-10">
          <motion.h1
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.62, ease: [0.16, 1, 0.3, 1] }}
            className="font-medium"
            style={{
              fontSize: 'clamp(26px, 2.8vw, 44px)',
              lineHeight: 1.06,
              letterSpacing: '-0.035em',
              color: 'var(--t1)',
              marginBottom: 14,
            }}
          >
            El mercado entero,<br />en un índice vivo.
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.60, ease: [0.16, 1, 0.3, 1], delay: 0.1 }}
            style={{ fontSize: 14, lineHeight: 1.65, color: 'var(--t3)', maxWidth: 340 }}
          >
            Indexamos cada plataforma de España y te decimos,
            en claro, si un coche está bien comprado.
          </motion.p>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.22, duration: 0.5 }}
            className="flex flex-col gap-3.5 mt-10"
          >
            {[
              '1.5M vehículos indexados en tiempo real',
              '27 mercados europeos comparados',
              'Datos observados, no estimados',
            ].map((feat, i) => (
              <div key={i} className="flex items-center gap-3">
                <div
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: '50%',
                    background: '#3B82F6',
                    flexShrink: 0,
                    boxShadow: '0 0 7px rgba(59,130,246,0.55)',
                  }}
                />
                <span style={{ fontSize: 13, color: 'var(--t3)', fontWeight: 500 }}>
                  {feat}
                </span>
              </div>
            ))}
          </motion.div>
        </div>

        {/* Footer — bottom */}
        <div className="relative z-10">
          <span style={{ fontSize: 11.5, color: 'var(--t4)', letterSpacing: '-0.01em' }}>
            cardeep © {new Date().getFullYear()}
          </span>
        </div>
      </div>

      {/* ── Right panel — form ──────────────────────────────────────── */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
        <div className="w-full max-w-[420px]">
          {children}
        </div>
      </div>
    </div>
  )
}

// ─── LoginPage ────────────────────────────────────────────────────────────────

export default function LoginPage() {
  const { login, isLoading } = useAuthContext()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: string })?.from ?? '/dashboard'

  const [email, setEmail]               = useState('')
  const [password, setPassword]         = useState('')
  const [keepLoggedIn, setKeepLoggedIn] = useState(false)
  const [error, setError]               = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await login(email, password)
      navigate(from, { replace: true })
    } catch {
      setError('Email o contraseña incorrectos')
    }
  }

  return (
    <AuthSplitLayout>
      <motion.div
        initial={{ opacity: 0, y: 22 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.48, ease: [0.16, 1, 0.3, 1] }}
      >
        <FormCard>
          {/* Header */}
          <div className="mb-7">
            <h1
              className="text-xl font-semibold mb-1.5"
              style={{ color: 'var(--t1)', letterSpacing: '-0.022em' }}
            >
              Bienvenido de nuevo
            </h1>
            <p className="text-sm" style={{ color: 'var(--t4)' }}>
              Accede a tu espacio de trabajo
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <Input
              label="Email"
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="tu@concesionario.com"
              icon={<Mail className="w-4 h-4" />}
            />

            {/* Password */}
            <PasswordInput
              label="Contraseña"
              value={password}
              onChange={v => setPassword(v)}
              autoComplete="current-password"
            />

            {/* Keep logged in + forgot */}
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={keepLoggedIn}
                  onChange={e => setKeepLoggedIn(e.target.checked)}
                  className="w-4 h-4 rounded cursor-pointer"
                />
                <span className="text-xs font-medium" style={{ color: 'var(--t3)' }}>
                  Mantener sesión
                </span>
              </label>
              <Link
                to="/reset"
                className="text-xs font-medium text-accent-blue hover:brightness-110 transition-all"
              >
                ¿Olvidaste la contraseña?
              </Link>
            </div>

            {/* Error */}
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="text-xs text-accent-rose bg-accent-rose/10 border border-accent-rose/20 rounded-lg px-3.5 py-2.5"
              >
                {error}
              </motion.div>
            )}

            {/* Submit */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={isLoading}
              className="w-full"
            >
              {isLoading ? 'Accediendo…' : 'Iniciar sesión'}
            </Button>
          </form>

          <p className="text-center text-xs mt-6" style={{ color: 'var(--t4)' }}>
            ¿No tienes cuenta?{' '}
            <Link
              to="/register"
              className="font-semibold text-accent-blue hover:brightness-110 transition-all"
            >
              Regístrate gratis
            </Link>
          </p>
        </FormCard>
      </motion.div>
    </AuthSplitLayout>
  )
}
