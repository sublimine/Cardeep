import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { LANDING_HTML, initLanding } from './portal/landingPortal'

/**
 * Landing — exact mirror of the :8777 portal landing (portal/index.html).
 *
 * The markup + vanilla engine live in ./portal/landingPortal.ts (verbatim from
 * the Claude-Design port). This is the thin React seam:
 *   - injects the portal markup via dangerouslySetInnerHTML,
 *   - runs the portal engine exactly once (StrictMode double-invokes effects;
 *     the once-guard keeps init from attaching listeners twice on the same DOM),
 *   - hands the engine a stable `navigate` so internal `/...` anchors become
 *     client-side SPA navigation instead of full reloads.
 *
 * No destructive cleanup: every listener the engine attaches lives on nodes
 * inside this div, so React's unmount removes them with the subtree.
 */
export default function Landing() {
  const navigate = useNavigate()
  const navRef = useRef(navigate)
  navRef.current = navigate
  const didInit = useRef(false)

  useEffect(() => {
    if (didInit.current) return
    didInit.current = true
    initLanding((to: string) => navRef.current(to))
  }, [])

  return <div dangerouslySetInnerHTML={{ __html: LANDING_HTML }} />
}
