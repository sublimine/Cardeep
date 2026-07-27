import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate, Link } from 'react-router-dom'
import { Mail, MailCheck } from 'lucide-react'
import Input from '../components/Input'
import Button from '../components/Button'
import { AuthSplitLayout, FormCard } from '../auth/LoginPage'

// ─── ResetPassword ────────────────────────────────────────────────────────────

export default function ResetPassword() {
  const navigate = useNavigate()
  const [email, setEmail]     = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent]       = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    // Simulate network delay — real endpoint: POST /api/v1/auth/reset
    await new Promise<void>(resolve => setTimeout(resolve, 900))
    setLoading(false)
    setSent(true)
  }

  return (
    <AuthSplitLayout>
      <AnimatePresence mode="wait">
        {sent ? (
          /* ── Success state ─────────────────────────────────────────── */
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.96 }}
            transition={{ duration: 0.38, ease: [0.16, 1, 0.3, 1] }}
          >
            <FormCard>
              <div className="flex flex-col items-center text-center py-4">
                {/* Icon */}
                <div
                  className="w-14 h-14 rounded-2xl flex items-center justify-center mb-6"
                  style={{
                    background: 'rgba(59,130,246,0.10)',
                    border: '1px solid rgba(59,130,246,0.18)',
                  }}
                >
                  <MailCheck className="w-7 h-7" style={{ color: '#3B82F6' }} />
                </div>

                <h1
                  className="text-xl font-semibold mb-2"
                  style={{ color: 'var(--t1)', letterSpacing: '-0.022em' }}
                >
                  Revisa tu bandeja
                </h1>
                <p
                  className="text-sm leading-relaxed mb-2"
                  style={{ color: 'var(--t4)', maxWidth: 300 }}
                >
                  Hemos enviado el enlace de recuperación a{' '}
                  <span className="font-semibold" style={{ color: 'var(--t2)' }}>
                    {email}
                  </span>
                </p>
                <p className="text-xs mb-8" style={{ color: 'var(--t4)' }}>
                  Si no ves el email, revisa la carpeta de spam.
                </p>

                <Button
                  variant="secondary"
                  size="md"
                  className="w-full"
                  onClick={() => navigate('/login')}
                >
                  Volver al inicio de sesión
                </Button>
              </div>
            </FormCard>
          </motion.div>
        ) : (
          /* ── Form state ────────────────────────────────────────────── */
          <motion.div
            key="form"
            initial={{ opacity: 0, y: 22 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.48, ease: [0.16, 1, 0.3, 1] }}
          >
            <FormCard>
              {/* Header */}
              <div className="mb-7">
                <h1
                  className="text-xl font-semibold mb-1.5"
                  style={{ color: 'var(--t1)', letterSpacing: '-0.022em' }}
                >
                  ¿Olvidaste la contraseña?
                </h1>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--t4)' }}>
                  Introduce el email de tu cuenta y te enviaremos un enlace para recuperarla.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                <Input
                  label="Email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="tu@concesionario.com"
                  icon={<Mail className="w-4 h-4" />}
                />

                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  loading={loading}
                  className="w-full"
                >
                  {loading ? 'Enviando…' : 'Enviar enlace de recuperación'}
                </Button>
              </form>

              <p className="text-center text-xs mt-6" style={{ color: 'var(--t4)' }}>
                Recuerdo mi contraseña.{' '}
                <Link
                  to="/login"
                  className="font-semibold text-accent-blue hover:brightness-110 transition-all"
                >
                  Iniciar sesión
                </Link>
              </p>
            </FormCard>
          </motion.div>
        )}
      </AnimatePresence>
    </AuthSplitLayout>
  )
}
