import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Shell from './layout/Shell'
import ProtectedRoute from './auth/ProtectedRoute'
import LoginPage from './auth/LoginPage'
import Landing from './pages/Landing'
import Marketplace from './pages/Marketplace'
import Dashboard from './pages/Dashboard'
import Vehicles from './pages/inventory'
import Kanban from './pages/Kanban'
import Contacts from './pages/Contacts'
import Deals from './pages/Deals'
import Inbox from './pages/Inbox'
import Publicaciones from './pages/Publicaciones'
import Calendar from './pages/Calendar'
import Mercado from './pages/Mercado'
import Settings from './pages/Settings'
import Inteligencia from './pages/Inteligencia'
import Arbitrage from './pages/Arbitrage'
import Api from './pages/Api'
import Analitica from './pages/Analitica'
import Register from './pages/Register'
import ResetPassword from './pages/ResetPassword'
import TwoStep from './pages/TwoStep'
import Invoices from './pages/Invoices'
import Pricing from './pages/Pricing'
import Notes from './pages/Notes'
import Profile from './pages/Profile'
import Support from './pages/Support'
// Chat.tsx (internal team-chat simulator) intentionally NOT imported (06-unified-crm-chat
// F3): decommissioned from the nav/routes, code left parked per the carta's decision.
import Assistant from './pages/Assistant'
import Motor from './pages/Motor'
import Terminal from './pages/Terminal'
import Marketing from './pages/Marketing'
import Wanted from './pages/Wanted'
import { useAuthContext } from './auth/AuthContext'

function RootRedirect() {
  const { isAuthenticated, isLoading } = useAuthContext()
  if (isLoading) return null
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <Landing />
}

/**
 * Fixed flat backdrop behind every page (tokens.css `.cx-mesh` sets `background: var(--bg-base)`).
 * The colored-orb mesh this used to render is permanently disabled by a global
 * `!important` CSS rule (`.cx-mesh > div { display: none }`) — dead on every route,
 * including /terminal, whose own override rule is redundant for the same reason.
 * Kept as an unstyled div (no JS children) rather than deleted outright: several
 * glass surfaces (`--glass-*`, `backdrop-filter`) are authored assuming this layer exists.
 */
function GlobalMesh() {
  return <div className="cx-mesh" aria-hidden />
}

export default function App() {
  return (
    <>
      <GlobalMesh />
      <Routes>
        {/* Public routes */}
        <Route path="/"         element={<RootRedirect />} />
        <Route path="/landing"  element={<Landing />} />
        <Route path="/marketplace" element={<Marketplace />} />
        <Route path="/login"    element={<LoginPage />} />
        <Route path="/register" element={<Register />} />
        <Route path="/reset"    element={<ResetPassword />} />
        <Route path="/2fa"      element={<TwoStep />} />
        {/* /check route deliberately removed (02-history-reports F0): the page
            (web/src/pages/Check.tsx) is quarantined until F3 rewires it to real
            data. Re-add here when F3 lands. */}

        {/* Protected app shell */}
        <Route
          element={
            <ProtectedRoute>
              <Shell />
            </ProtectedRoute>
          }
        >
          <Route path="dashboard"  element={<Dashboard />} />
          <Route path="vehicles"   element={<Vehicles />} />
          <Route path="kanban"     element={<Kanban />} />
          <Route path="contacts"   element={<Contacts />} />
          <Route path="deals"      element={<Deals />} />
          <Route path="inbox"      element={<Inbox />} />
          <Route path="publicaciones" element={<Publicaciones />} />
          <Route path="calendar"   element={<Calendar />} />
          <Route path="finance"    element={<Mercado />} />
          <Route path="inteligencia" element={<Inteligencia />} />
          <Route path="arbitrage"  element={<Arbitrage />} />
          <Route path="api"        element={<Api />} />
          <Route path="analitica"  element={<Analitica />} />
          <Route path="marketing"  element={<Marketing />} />
          {/* 08-forum-community F3: "Se busca" board. /community (foro) lands in F5,
              behind masa-crítica gate per the carta's own priority order (§3/§9). */}
          <Route path="community/wanted" element={<Wanted />} />
          <Route path="invoices"   element={<Invoices />} />
          <Route path="pricing"    element={<Pricing />} />
          <Route path="notes"      element={<Notes />} />
          <Route path="profile"    element={<Profile />} />
          <Route path="support"    element={<Support />} />
          {/* /chat route removed (06-unified-crm-chat F3): see import comment above. */}
          <Route path="assistant"  element={<Assistant />} />
          <Route path="motor"      element={<Motor />} />
          <Route path="terminal"   element={<Terminal />} />
          <Route path="settings"   element={<Settings />} />
          <Route path="*"          element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </>
  )
}
