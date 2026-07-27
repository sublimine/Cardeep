import React, { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { useNavigate, Link } from 'react-router-dom'
import { cn } from '../lib/cn'
import Button from '../components/Button'
import { AuthSplitLayout, FormCard } from '../auth/LoginPage'

// ─── TwoStep ──────────────────────────────────────────────────────────────────

const DIGIT_COUNT = 6

export default function TwoStep() {
  const navigate  = useNavigate()
  const [digits, setDigits]   = useState<string[]>(Array(DIGIT_COUNT).fill(''))
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState<string | null>(null)
  const refs = useRef<Array<HTMLInputElement | null>>(Array(DIGIT_COUNT).fill(null))

  function handleDigit(index: number, raw: string) {
    // Accept only a single numeric character
    const digit = raw.replace(/\D/g, '').slice(-1)
    const next = [...digits]
    next[index] = digit
    setDigits(next)
    setError(null)
    // Auto-advance focus
    if (digit && index < DIGIT_COUNT - 1) {
      refs.current[index + 1]?.focus()
    }
  }

  function handleKeyDown(index: number, e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Backspace' && !digits[index] && index > 0) {
      refs.current[index - 1]?.focus()
    }
    if (e.key === 'ArrowLeft' && index > 0) {
      refs.current[index - 1]?.focus()
    }
    if (e.key === 'ArrowRight' && index < DIGIT_COUNT - 1) {
      refs.current[index + 1]?.focus()
    }
  }

  function handlePaste(e: React.ClipboardEvent<HTMLDivElement>) {
    e.preventDefault()
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, DIGIT_COUNT)
    const next = Array(DIGIT_COUNT).fill('') as string[]
    pasted.split('').forEach((d, i) => { next[i] = d })
    setDigits(next)
    setError(null)
    const focusIdx = Math.min(pasted.length, DIGIT_COUNT - 1)
    refs.current[focusIdx]?.focus()
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const code = digits.join('')
    if (code.length < DIGIT_COUNT) {
      setError('Introduce los 6 dígitos del código')
      return
    }
    setLoading(true)
    // Simulate verification — real endpoint: POST /api/v1/auth/verify-otp
    await new Promise<void>(resolve => setTimeout(resolve, 800))
    navigate('/dashboard', { replace: true })
  }

  const digitCls = cn(
    'h-12 w-full text-center text-lg font-semibold rounded-lg',
    'text-text-primary bg-glass-subtle border transition-all duration-200',
    'focus:outline-none focus:ring-2 focus:ring-offset-0',
    'focus:ring-accent-blue/30 focus:border-border-active border-border-subtle',
    'selection:bg-accent-blue/20',
  )

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
              Verificación en dos pasos
            </h1>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--t4)' }}>
              Hemos enviado un código de 6 dígitos a tu dispositivo. Introdúcelo a continuación.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* OTP digit inputs */}
            <div>
              <label
                className="block text-xs font-medium text-text-secondary mb-3 uppercase tracking-wide"
              >
                Código de seguridad
              </label>
              <div
                className="grid grid-cols-6 gap-2.5"
                onPaste={handlePaste}
              >
                {digits.map((d, i) => (
                  <motion.input
                    key={i}
                    ref={el => { refs.current[i] = el }}
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={1}
                    value={d}
                    autoFocus={i === 0}
                    onChange={e => handleDigit(i, e.target.value)}
                    onKeyDown={e => handleKeyDown(i, e)}
                    aria-label={`Dígito ${i + 1} de ${DIGIT_COUNT}`}
                    className={digitCls}
                    animate={
                      error && !d
                        ? { x: [0, -4, 4, -3, 3, 0] }
                        : { x: 0 }
                    }
                    transition={{ duration: 0.35, ease: 'easeInOut' }}
                  />
                ))}
              </div>
            </div>

            {/* Error */}
            {error && (
              <motion.p
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-xs text-accent-rose -mt-2"
              >
                {error}
              </motion.p>
            )}

            {/* Submit */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={loading}
              className="w-full"
            >
              {loading ? 'Verificando…' : 'Verificar cuenta'}
            </Button>
          </form>

          <p className="text-center text-xs mt-6" style={{ color: 'var(--t4)' }}>
            ¿No has recibido el código?{' '}
            <button
              type="button"
              className="font-semibold text-accent-blue hover:brightness-110 transition-all bg-transparent border-0 p-0 cursor-pointer"
              onClick={() => {
                setDigits(Array(DIGIT_COUNT).fill(''))
                setError(null)
                refs.current[0]?.focus()
              }}
            >
              Reenviar
            </button>
            {' · '}
            <Link
              to="/login"
              className="font-semibold text-accent-blue hover:brightness-110 transition-all"
            >
              Volver
            </Link>
          </p>
        </FormCard>
      </motion.div>
    </AuthSplitLayout>
  )
}
