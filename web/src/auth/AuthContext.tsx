import React, { createContext, useCallback, useContext, useEffect, useState } from 'react'
import {
  api,
  setAccessToken,
  setTenantId,
  setTokenExpiry,
  getStoredToken,
  getStoredTenantId,
  isTokenValid,
} from '../api/client'
import type { User } from '../types'

// AUTH-0 (00-MASTER.md §2 C-3): DEV_BYPASS is gone — this context always talks to the real
// /auth/* backend (services/api/routers/auth.py). Three other cartas (03-F1, 05-F3, 08-F1)
// each independently planned to recable this file; AUTH-0 is the single time it happens.

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name?: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

interface AuthResponse { token: string; expires_in: number; user: User }

/** The backend returns tenant_id (snake_case); normalize onto the frontend's tenantId. */
function hydrateUser(rawUser: User): User {
  const raw = rawUser as unknown as Record<string, unknown>
  return { ...rawUser, tenantId: (raw.tenantId ?? raw.tenant_id ?? '') as string }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    // Restore session from localStorage on init.
    if (isTokenValid()) {
      const tid = getStoredTenantId()
      if (tid) setTenantId(tid)
      return { user: null, isLoading: true, isAuthenticated: false }
    }
    return { user: null, isLoading: false, isAuthenticated: false }
  })

  // Hydrate user from /auth/me if we have a stored token.
  useEffect(() => {
    if (!isTokenValid()) return
    api.get<{ user: User }>('/auth/me')
      .then(data => setState({ user: hydrateUser(data.user), isLoading: false, isAuthenticated: true }))
      .catch(() => {
        setAccessToken(null)
        setState({ user: null, isLoading: false, isAuthenticated: false })
      })
  }, [])

  const logout = useCallback(() => {
    const token = getStoredToken()
    if (token) {
      // Best-effort server-side session revocation via a RAW fetch — deliberately not
      // api.post(), whose 401 handling dispatches 'auth:unauthorized', which this very
      // function handles below; routing the revocation call through api.post() here would
      // re-enter logout() on any failure and loop.
      fetch('/api/v1/auth/logout', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      }).catch(() => {})
    }
    setAccessToken(null)
    setTenantId(null)
    setState({ user: null, isLoading: false, isAuthenticated: false })
  }, [])

  const applySession = useCallback((data: AuthResponse) => {
    const user = hydrateUser(data.user)
    setAccessToken(data.token)
    setTokenExpiry(data.expires_in)
    setTenantId(user.tenantId || null)
    setState({ user, isLoading: false, isAuthenticated: true })
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    setState(s => ({ ...s, isLoading: true }))
    try {
      const data = await api.post<AuthResponse>('/auth/login', { email, password })
      applySession(data)
    } catch (err) {
      setState(s => ({ ...s, isLoading: false }))
      throw err
    }
  }, [applySession])

  const register = useCallback(async (email: string, password: string, name?: string) => {
    setState(s => ({ ...s, isLoading: true }))
    try {
      const data = await api.post<AuthResponse>('/auth/register', { email, password, name: name ?? '' })
      applySession(data)
    } catch (err) {
      setState(s => ({ ...s, isLoading: false }))
      throw err
    }
  }, [applySession])

  useEffect(() => {
    window.addEventListener('auth:unauthorized', logout)
    return () => window.removeEventListener('auth:unauthorized', logout)
  }, [logout])

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuthContext(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuthContext must be used inside AuthProvider')
  return ctx
}
