import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthContext } from './AuthContext'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthContext()
  const location = useLocation()

  // 08-forum-community F5 fix (found while verifying real-browser E2E for this pilar,
  // affects every authenticated route, not just this one): AuthProvider briefly reports
  // isAuthenticated=false while it verifies a stored token against /auth/me on mount
  // (isLoading=true during that window). Without this check, ANY hard navigation/reload
  // with a perfectly valid session bounced straight to /login — RootRedirect (App.tsx)
  // already guards this exact race; ProtectedRoute did not, which was the inconsistency.
  if (isLoading) return null

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />
  }

  return <>{children}</>
}
