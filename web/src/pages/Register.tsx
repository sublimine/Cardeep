import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuthContext } from '../auth/AuthContext'
import { useNavigate, Link } from 'react-router-dom'
import { Mail, User } from 'lucide-react'
import Input from '../components/Input'
import Button from '../components/Button'
import { AuthSplitLayout, FormCard, PasswordInput } from '../auth/LoginPage'
import { ApiError } from '../api/client'

// ─── Register ─────────────────────────────────────────────────────────────────

export default function Register() {
  const { register } = useAuthContext()
  const navigate = useNavigate()

  const [firstName, setFirstName]           = useState('')
  const [lastName, setLastName]             = useState('')
  const [email, setEmail]                   = useState('')
  const [password, setPassword]             = useState('')
  const [confirmPwd, setConfirmPwd]         = useState('')
  const [terms, setTerms]                   = useState(false)
  const [loading, setLoading]               = useState(false)
  const [error, setError]                   = useState<string | null>(null)

  const pwdMismatch =
    confirmPwd.length > 0 && password !== confirmPwd

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    if (pwdMismatch) {
      setError('Las contraseñas no coinciden')
      return
    }
    if (!terms) {
      setError('Debes aceptar los términos y condiciones')
      return
    }

    setLoading(true)
    try {
      await register(email, password, `${firstName} ${lastName}`.trim())
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 409
          ? 'Ya existe una cuenta con ese email'
          : 'No se pudo crear la cuenta. Inténtalo de nuevo.',
      )
      setLoading(false)
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
              Crea tu cuenta
            </h1>
            <p className="text-sm" style={{ color: 'var(--t4)' }}>
              Empieza gratis. Sin tarjeta de crédito.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name row */}
            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Nombre"
                type="text"
                autoComplete="given-name"
                required
                value={firstName}
                onChange={e => setFirstName(e.target.value)}
                placeholder="Ana"
                icon={<User className="w-4 h-4" />}
              />
              <Input
                label="Apellido"
                type="text"
                autoComplete="family-name"
                required
                value={lastName}
                onChange={e => setLastName(e.target.value)}
                placeholder="García"
              />
            </div>

            {/* Email */}
            <Input
              label="Email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="ana@concesionario.com"
              icon={<Mail className="w-4 h-4" />}
            />

            {/* Password */}
            <PasswordInput
              label="Contraseña"
              value={password}
              onChange={v => setPassword(v)}
              autoComplete="new-password"
              placeholder="Mínimo 10 caracteres"
            />

            {/* Confirm password */}
            <PasswordInput
              label="Confirmar contraseña"
              value={confirmPwd}
              onChange={v => setConfirmPwd(v)}
              autoComplete="new-password"
              placeholder="Repite la contraseña"
              error={pwdMismatch ? 'Las contraseñas no coinciden' : undefined}
            />

            {/* Terms */}
            <label className="flex items-start gap-3 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={terms}
                onChange={e => setTerms(e.target.checked)}
                className="mt-0.5 w-4 h-4 rounded cursor-pointer shrink-0"
              />
              <span className="text-xs leading-relaxed" style={{ color: 'var(--t4)' }}>
                Acepto los{' '}
                <span className="font-semibold" style={{ color: 'var(--t2)' }}>
                  Términos y condiciones
                </span>
                {' '}y la{' '}
                <span className="font-semibold" style={{ color: 'var(--t2)' }}>
                  Política de privacidad
                </span>
              </span>
            </label>

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
              loading={loading}
              className="w-full"
            >
              {loading ? 'Creando cuenta…' : 'Crear cuenta'}
            </Button>
          </form>

          <p className="text-center text-xs mt-6" style={{ color: 'var(--t4)' }}>
            ¿Ya tienes cuenta?{' '}
            <Link
              to="/login"
              className="font-semibold text-accent-blue hover:brightness-110 transition-all"
            >
              Inicia sesión
            </Link>
          </p>
        </FormCard>
      </motion.div>
    </AuthSplitLayout>
  )
}
